-- 001_create_shops.sql
CREATE TABLE IF NOT EXISTS shops (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    platform VARCHAR(20) NOT NULL,
    platform_shop_id VARCHAR(100),
    app_key VARCHAR(100),
    app_secret VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMPTZ,
    status SMALLINT DEFAULT 1,
    sync_enabled BOOLEAN DEFAULT FALSE,
    sync_interval_minutes INT DEFAULT 15,
    last_sync_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_shops_platform ON shops(platform);
CREATE INDEX IF NOT EXISTS idx_shops_status ON shops(status);
CREATE INDEX IF NOT EXISTS idx_shops_deleted_at ON shops(deleted_at);

COMMENT ON TABLE shops IS '店铺表';
COMMENT ON COLUMN shops.platform IS '平台标识: taobao/jd/pdd';
COMMENT ON COLUMN shops.status IS '1=正常 0=禁用 -1=过期';
