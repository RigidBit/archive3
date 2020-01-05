CREATE TABLE "data"
(
	"id" serial NOT NULL,
	"url_id" integer NOT NULL,
	"hash" char(64) NOT NULL,
	"block_id" INTEGER NULL,
	"removed" boolean NOT NULL DEFAULT false,
	"timestamp" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (id)
);

CREATE INDEX "ix_data_url_id_removed_timestamp" ON "data" ("url_id", "removed", "timestamp");

CREATE TABLE "submissions"
(
	"id" serial NOT NULL,
	"url" varchar(65535) NOT NULL,
	"ip" varchar(45) NOT NULL DEFAULT '',
	"processed" boolean NOT NULL DEFAULT false,
	"ready" boolean NOT NULL DEFAULT false,
	"timestamp" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (id)
);

CREATE INDEX "ix_submissions_processed_timestamp" ON "submissions" ("processed", "timestamp");
CREATE INDEX "ix_submissions_processed_ready" ON "submissions" ("processed", "ready");

CREATE TABLE "urls"
(
	"id" serial NOT NULL,
	"url" varchar(65535) NOT NULL,
	"settings" varchar(65535) NOT NULL DEFAULT '',
	"errors" integer NOT NULL DEFAULT 0,
	"removed" boolean NOT NULL DEFAULT false,
	"timestamp" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"timestamp_queued" timestamp NULL,
	"timestamp_updated" timestamp NULL,
	PRIMARY KEY (id)
);

CREATE INDEX "ix_urls_url_removed" ON "urls" ("url", "removed");
CREATE INDEX "ix_urls_removed_timestamp_queued" ON "urls" ("removed", "timestamp_queued");
CREATE INDEX "ix_urls_removed_timestamp_updated" ON "urls" ("removed", "timestamp_updated");

ALTER TABLE data ADD CONSTRAINT fk_url_id FOREIGN KEY (url_id) REFERENCES urls(id) ON DELETE CASCADE;
