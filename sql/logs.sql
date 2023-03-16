CREATE TABLE IF NOT EXISTS public.logs (
    "id" serial NOT NULL,
    "log_time" text,
    "log_message" text,
    CONSTRAINT "logs_pkey" PRIMARY KEY ("id")
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."logs"
    OWNER to postgres;

CREATE TABLE IF NOT EXISTS public.anomalies (
    "id" serial NOT NULL,
    "log_time" text,
    "log_message" text,
    "anomaly_score" float,
    "false_positive" boolean,
    CONSTRAINT "logs_pkey" PRIMARY KEY ("id")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."anomalies"
    OWNER to postgres;


CREATE INDEX ON public.anomalies (id);