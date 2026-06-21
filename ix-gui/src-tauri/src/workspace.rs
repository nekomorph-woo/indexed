//! WorkspaceIo 命令实现（8 个）。
//!
//! 所有命令通过 State<'_, AppState> 拿 workspace_root，所有路径相对它解析。
//! 读操作为主；list_agents/list_clis 会聚合 SPEC.yaml + 目录扫描结果。

use crate::error::{AppError, Result};
use crate::models::{
    AgentInfo, AgentSpec, CliInfo, CliSpec, Manifest, RunArtifactFile, RunDetail, RunStatus,
    RunSummary, RunTrigger, RunYaml, SpecStatus, TreeNode, TreeNodeKind,
};
use crate::state::AppState;
use std::path::Path;
use tauri::State;

const SKIP_DIRS: &[&str] = &[
    "node_modules",
    "target",
    "dist",
    ".git",
    ".vite",
    "__pycache__",
    "runs", // runs/ 子目录单独走 list_runs
];

// ─────────────────────────────────────────────────────
// list_agents / list_clis
// ─────────────────────────────────────────────────────

#[tauri::command]
pub async fn list_agents(state: State<'_, AppState>) -> Result<Vec<AgentInfo>> {
    let agents_dir = state.workspace_root.join("ix-agents");
    let mut agents = vec![];
    if !agents_dir.is_dir() {
        return Ok(agents);
    }
    for entry in std::fs::read_dir(&agents_dir)? {
        let entry = entry?;
        let name = entry.file_name().to_string_lossy().to_string();
        if !name.starts_with("ix-") || !name.ends_with("-agent") {
            continue;
        }
        let path = entry.path();
        if !path.is_dir() {
            continue;
        }
        agents.push(parse_agent_info(&name, &path)?);
    }
    agents.sort_by(|a, b| a.name.cmp(&b.name));
    Ok(agents)
}

#[tauri::command]
pub async fn list_clis(state: State<'_, AppState>) -> Result<Vec<CliInfo>> {
    let artifacts_dir = state.workspace_root.join("artifacts");
    let mut clis = vec![];
    if !artifacts_dir.is_dir() {
        return Ok(clis);
    }
    for entry in std::fs::read_dir(&artifacts_dir)? {
        let entry = entry?;
        let name = entry.file_name().to_string_lossy().to_string();
        if !name.starts_with("ix-") || !name.ends_with("-cli") {
            continue;
        }
        let path = entry.path();
        if !path.is_dir() {
            continue;
        }
        clis.push(parse_cli_info(&name, &path)?);
    }
    clis.sort_by(|a, b| a.name.cmp(&b.name));
    Ok(clis)
}

fn parse_agent_info(name: &str, path: &Path) -> Result<AgentInfo> {
    let spec_path = path.join("SPEC.yaml");
    let manifest_path = path.join("manifest.yaml");
    let has_manifest = manifest_path.is_file();

    let (domain, one_liner, status, has_thinking, steps_summary, required_params) = if spec_path.is_file() {
        let spec: AgentSpec = serde_yaml::from_str(&std::fs::read_to_string(&spec_path)?)?;
        let steps_summary = if spec.steps.is_empty() {
            "(无 steps)".to_string()
        } else {
            spec.steps.join(" → ")
        };
        (
            spec.domain,
            spec.one_liner,
            spec.status,
            spec.has_thinking,
            steps_summary,
            spec.params_required,
        )
    } else {
        (
            "(无 SPEC)".to_string(),
            "(无 SPEC.yaml)".to_string(),
            SpecStatus::Planned,
            false,
            "(无 SPEC)".to_string(),
            vec![],
        )
    };

    let runs_dir = path.join("runs");
    let recent_run_count = if runs_dir.is_dir() {
        std::fs::read_dir(&runs_dir)?
            .filter_map(|e| e.ok())
            .filter(|e| e.path().is_dir())
            .count() as i64
    } else {
        0
    };

    Ok(AgentInfo {
        name: name.to_string(),
        domain,
        one_liner,
        status,
        has_thinking,
        has_manifest,
        steps_summary,
        required_params,
        recent_run_count,
    })
}

fn parse_cli_info(name: &str, path: &Path) -> Result<CliInfo> {
    let spec_path = path.join("SPEC.yaml");
    let has_spec_yaml = spec_path.is_file();
    let (domain, one_liner, status, subcommands) = if has_spec_yaml {
        let spec: CliSpec = serde_yaml::from_str(&std::fs::read_to_string(&spec_path)?)?;
        let subcommands: Vec<String> = spec.commands.iter().map(|c| c.name.clone()).collect();
        (spec.domain, spec.one_liner, spec.status, subcommands)
    } else {
        (
            "(无 SPEC)".to_string(),
            "(无 SPEC.yaml)".to_string(),
            SpecStatus::Planned,
            vec![],
        )
    };
    Ok(CliInfo {
        name: name.to_string(),
        domain,
        one_liner,
        status,
        subcommands,
        has_spec_yaml,
    })
}

// ─────────────────────────────────────────────────────
// read_manifest / read_agent_spec / read_cli_spec
// ─────────────────────────────────────────────────────

#[tauri::command]
pub async fn read_manifest(agent: String, state: State<'_, AppState>) -> Result<Manifest> {
    let path = state
        .workspace_root
        .join("ix-agents")
        .join(&agent)
        .join("manifest.yaml");
    if !path.is_file() {
        return Err(AppError::NotFound(path.to_string_lossy().to_string()));
    }
    let content = std::fs::read_to_string(&path)?;
    Ok(serde_yaml::from_str(&content)?)
}

#[tauri::command]
pub async fn read_agent_spec(agent: String, state: State<'_, AppState>) -> Result<AgentSpec> {
    let path = state
        .workspace_root
        .join("ix-agents")
        .join(&agent)
        .join("SPEC.yaml");
    if !path.is_file() {
        return Err(AppError::NotFound(path.to_string_lossy().to_string()));
    }
    let content = std::fs::read_to_string(&path)?;
    Ok(serde_yaml::from_str(&content)?)
}

#[tauri::command]
pub async fn read_cli_spec(cli: String, state: State<'_, AppState>) -> Result<CliSpec> {
    let path = state
        .workspace_root
        .join("artifacts")
        .join(&cli)
        .join("SPEC.yaml");
    if !path.is_file() {
        return Err(AppError::NotFound(path.to_string_lossy().to_string()));
    }
    let content = std::fs::read_to_string(&path)?;
    Ok(serde_yaml::from_str(&content)?)
}

// ─────────────────────────────────────────────────────
// list_runs / read_run
// ─────────────────────────────────────────────────────

#[tauri::command]
pub async fn list_runs(agent: String, state: State<'_, AppState>) -> Result<Vec<RunSummary>> {
    let runs_dir = state
        .workspace_root
        .join("ix-agents")
        .join(&agent)
        .join("runs");
    let mut summaries = vec![];
    if !runs_dir.is_dir() {
        return Ok(summaries);
    }
    for entry in std::fs::read_dir(&runs_dir)? {
        let entry = entry?;
        let path = entry.path();
        if !path.is_dir() {
            continue;
        }
        let run_yaml = path.join("run.yaml");
        if !run_yaml.is_file() {
            continue;
        }
        let yaml: RunYaml = serde_yaml::from_str(&std::fs::read_to_string(&run_yaml)?)?;
        summaries.push(RunSummary {
            run_id: yaml.run_id,
            agent_id: yaml.agent_id,
            status: yaml.status,
            trigger: yaml.trigger,
            started_at: yaml.started_at,
            steps_total: yaml.steps_completed.len() as i64, // 简化：用 completed 计数
            steps_completed: yaml.steps_completed,
            next_step: yaml.next_step,
        });
    }
    summaries.sort_by(|a, b| b.started_at.cmp(&a.started_at));
    Ok(summaries)
}

#[tauri::command]
pub async fn read_run(
    agent: String,
    run_id: String,
    state: State<'_, AppState>,
) -> Result<RunDetail> {
    let run_dir = state
        .workspace_root
        .join("ix-agents")
        .join(&agent)
        .join("runs")
        .join(&run_id);
    if !run_dir.is_dir() {
        return Err(AppError::NotFound(run_dir.to_string_lossy().to_string()));
    }
    let yaml: RunYaml = serde_yaml::from_str(&std::fs::read_to_string(run_dir.join("run.yaml"))?)?;
    let summary = RunSummary {
        run_id: yaml.run_id,
        agent_id: yaml.agent_id,
        status: yaml.status,
        trigger: yaml.trigger,
        started_at: yaml.started_at,
        steps_total: yaml.steps_completed.len() as i64,
        steps_completed: yaml.steps_completed,
        next_step: yaml.next_step,
    };
    let output_files = list_run_artifacts(&run_dir.join("output"), &run_dir, "output")?;
    let thinking_files =
        list_run_artifacts(&run_dir.join("work").join("thinking"), &run_dir, "work/thinking")?;
    let raw_files = list_run_artifacts(&run_dir.join("work").join("raw"), &run_dir, "work/raw")?;

    Ok(RunDetail {
        summary,
        params: yaml.params,
        output_files,
        thinking_files,
        raw_files,
    })
}

fn list_run_artifacts(dir: &Path, run_dir: &Path, _kind: &str) -> Result<Vec<RunArtifactFile>> {
    let mut files = vec![];
    if !dir.is_dir() {
        return Ok(files);
    }
    for entry in walkdir::WalkDir::new(dir).max_depth(2) {
        let entry = entry?;
        if !entry.file_type().is_file() {
            continue;
        }
        let path = entry.path();
        let rel_path = path
            .strip_prefix(run_dir)
            .map(|p| p.to_string_lossy().to_string())
            .unwrap_or_default();
        let name = entry.file_name().to_string_lossy().to_string();
        let size = entry.metadata().map(|m| m.len()).unwrap_or(0);
        let ext = path
            .extension()
            .map(|e| format!(".{}", e.to_string_lossy()))
            .unwrap_or_default();
        // 文本文件读内容，二进制/超大文件返回 None
        let content = if size < 64 * 1024 && is_text_ext(&ext) {
            std::fs::read_to_string(path).ok()
        } else {
            None
        };
        files.push(RunArtifactFile {
            rel_path,
            name,
            size,
            content,
            ext,
        });
    }
    Ok(files)
}

fn is_text_ext(ext: &str) -> bool {
    matches!(
        ext,
        ".md" | ".txt" | ".yaml" | ".yml" | ".json" | ".csv" | ".html" | ".log" | ".py" | ".sh"
    )
}

// ─────────────────────────────────────────────────────
// read_workspace_tree
// ─────────────────────────────────────────────────────

#[tauri::command]
pub async fn read_workspace_tree(state: State<'_, AppState>) -> Result<TreeNode> {
    let root = &state.workspace_root;
    let root_name = root
        .file_name()
        .map(|n| n.to_string_lossy().to_string())
        .unwrap_or_else(|| "indexed".to_string());
    let node = build_tree_node(root, "", &root_name, TreeNodeKind::Bucket, 0)?;
    Ok(node)
}

fn build_tree_node(
    path: &Path,
    rel_path: &str,
    name: &str,
    kind: TreeNodeKind,
    depth: usize,
) -> Result<TreeNode> {
    const MAX_DEPTH: usize = 3;

    let mut node = TreeNode {
        name: name.to_string(),
        path: rel_path.to_string(),
        kind,
        children: vec![],
    };

    if !path.is_dir() || depth >= MAX_DEPTH {
        return Ok(node);
    }

    let mut children: Vec<TreeNode> = vec![];
    for entry in std::fs::read_dir(path)? {
        let entry = entry?;
        let entry_path = entry.path();
        let entry_name = entry.file_name().to_string_lossy().to_string();

        // 跳过隐藏文件和排除目录
        if entry_name.starts_with('.') || SKIP_DIRS.contains(&entry_name.as_str()) {
            continue;
        }

        let new_rel = if rel_path.is_empty() {
            entry_name.clone()
        } else {
            format!("{}/{}", rel_path, entry_name)
        };

        let is_dir = entry_path.is_dir();
        let child_kind = if is_top_level_bucket(rel_path, &entry_name) {
            TreeNodeKind::Bucket
        } else if is_dir {
            TreeNodeKind::Dir
        } else {
            TreeNodeKind::File
        };

        // 桶级（depth=0 的子）展开到 MAX_DEPTH；文件不深入
        let child = build_tree_node(&entry_path, &new_rel, &entry_name, child_kind, depth + 1)?;
        children.push(child);
    }

    children.sort_by(|a, b| {
        // 目录在前，文件在后；同类按名排序
        let a_is_dir = !matches!(a.kind, TreeNodeKind::File);
        let b_is_dir = !matches!(b.kind, TreeNodeKind::File);
        b_is_dir
            .cmp(&a_is_dir)
            .then_with(|| a.name.cmp(&b.name))
    });
    node.children = children;
    Ok(node)
}

fn is_top_level_bucket(parent_rel: &str, name: &str) -> bool {
    if !parent_rel.is_empty() {
        return false;
    }
    matches!(
        name,
        "_shared" | "reports" | "research" | "artifacts" | "ix-agents"
    )
}

// 让 unused imports 不告警（RunStatus/RunTrigger 用于 models，这里只做 serde 标记）
#[allow(dead_code)]
fn _types_marker(_: RunStatus, _: RunTrigger) {}
