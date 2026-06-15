-- Agent 相关数据库表
-- 由 agent-orchestrator 服务使用

-- 对话会话表
CREATE TABLE IF NOT EXISTS agent_sessions (
    session_id VARCHAR(64) PRIMARY KEY,
    user_id BIGINT NOT NULL,
    title VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_user ON agent_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_status ON agent_sessions(status);

-- 黑板条目持久化表（审计与回放）
CREATE TABLE IF NOT EXISTS blackboard_entries (
    id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL REFERENCES agent_sessions(session_id),
    entry_type VARCHAR(30) NOT NULL,
    key VARCHAR(255) NOT NULL,
    value JSONB NOT NULL,
    author_agent VARCHAR(50) NOT NULL,
    version INT DEFAULT 1,
    parent_version VARCHAR(64),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_bb_entries_session ON blackboard_entries(session_id);
CREATE INDEX IF NOT EXISTS idx_bb_entries_type ON blackboard_entries(session_id, entry_type);
CREATE INDEX IF NOT EXISTS idx_bb_entries_author ON blackboard_entries(author_agent);

-- Agent 执行日志表
CREATE TABLE IF NOT EXISTS agent_execution_logs (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL REFERENCES agent_sessions(session_id),
    agent_name VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    model_used VARCHAR(100),
    tokens_input INT,
    tokens_output INT,
    cost_usd DECIMAL(10,6),
    duration_ms INT,
    status VARCHAR(20),
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_agent_logs_session ON agent_execution_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_agent_logs_agent ON agent_execution_logs(agent_name);

-- 任务计划表
CREATE TABLE IF NOT EXISTS agent_task_plans (
    plan_id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL REFERENCES agent_sessions(session_id),
    original_intent TEXT NOT NULL,
    plan_data JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'created',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- 子任务表
CREATE TABLE IF NOT EXISTS agent_subtasks (
    task_id VARCHAR(64) PRIMARY KEY,
    plan_id VARCHAR(64) NOT NULL REFERENCES agent_task_plans(plan_id),
    agent_name VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    dependencies JSONB DEFAULT '[]',
    status VARCHAR(20) DEFAULT 'pending',
    result JSONB,
    revision_count INT DEFAULT 0,
    max_revisions INT DEFAULT 3,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_subtasks_plan ON agent_subtasks(plan_id);
