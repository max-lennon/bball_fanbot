CREATE TABLE "users" (
  "id" varchar PRIMARY KEY,
  "username" varchar NOT NULL,
  "flair_1" varchar,
  "flair_2" varchar,
  "created_at" timestamp
);

CREATE TABLE "posts" (
  "id" varchar PRIMARY KEY,
  "title" varchar NOT NULL,
  "body" text,
  "user_id" varchar NOT NULL,
  "category" varchar,
  "upvotes" integer,
  "created_at" timestamp
);

CREATE TABLE "comments" (
  "id" varchar PRIMARY KEY,
  "author" varchar NOT NULL,
  "post_id" varchar NOT NULL,
  "parent_id" varchar,
  "body" text,
  "upvotes" integer,
  "created_at" timestamp
);

CREATE TABLE "teams" (
  "team_name" varchar PRIMARY KEY,
  "conference" varchar NOT NULL,
  "wins" integer,
  "losses" integer
);

CREATE TABLE "players" (
  "player_name" varchar,
  "team_name" varchar
);

CREATE TABLE "games" (
  "home" varchar,
  "away" varchar,
  "home_score" integer,
  "away_score" integer,
  "game_thread" varchar,
  "post_thread" varchar,
  "when_played" timestamp
);

COMMENT ON COLUMN "posts"."body" IS 'Content of the post';

COMMENT ON COLUMN "posts"."category" IS 'Type of post, e.g. game thread, discusssion, news update';

ALTER TABLE "teams" ADD CONSTRAINT "home_team" FOREIGN KEY ("team_name") REFERENCES "games" ("home") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "teams" ADD CONSTRAINT "away_team" FOREIGN KEY ("team_name") REFERENCES "games" ("away") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "posts" ADD CONSTRAINT "game_thread" FOREIGN KEY ("id") REFERENCES "games" ("game_thread") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "posts" ADD CONSTRAINT "post_thread" FOREIGN KEY ("id") REFERENCES "games" ("post_thread") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "users" ADD CONSTRAINT "post_author" FOREIGN KEY ("id") REFERENCES "posts" ("user_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "users" ADD CONSTRAINT "comment_author" FOREIGN KEY ("id") REFERENCES "comments" ("author") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "posts" ADD CONSTRAINT "commented_on" FOREIGN KEY ("id") REFERENCES "comments" ("post_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "comments" ADD CONSTRAINT "parent_of" FOREIGN KEY ("parent_id") REFERENCES "comments" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "teams" ADD CONSTRAINT "user_team_1" FOREIGN KEY ("team_name") REFERENCES "users" ("flair_1") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "teams" ADD CONSTRAINT "user_team_2" FOREIGN KEY ("team_name") REFERENCES "users" ("flair_2") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "teams" ADD CONSTRAINT "player_team" FOREIGN KEY ("team_name") REFERENCES "players" ("team_name") DEFERRABLE INITIALLY IMMEDIATE;

-- Defer constraint checking for INSERT
BEGIN;
SET CONSTRAINTS ALL DEFERRED;

INSERT INTO "teams" ("team_name", "conference", "wins", "losses")
VALUES
  ('Duke', 'ACC', 29, 2),
  ('Virginia', 'ACC', 27, 4),
  ('Miami', 'ACC', 24, 7),
  ('North Carolina', 'ACC', 24, 7),
  ('Clemson', 'ACC', 22, 9),
  ('Louisville', 'ACC', 22, 9),
  ('NC State', 'ACC', 19, 12),
  ('Florida State', 'ACC', 17, 14),
  ('California', 'ACC', 21, 10),
  ('Stanford', 'ACC', 20, 11),
  ('SMU', 'ACC', 19, 12),
  ('Virginia Tech', 'ACC', 19, 12),
  ('Wake Forest', 'ACC', 16, 15),
  ('Syracuse', 'ACC', 15, 16),
  ('Pittsburgh', 'ACC', 12, 19),
  ('Notre Dame', 'ACC', 13, 18),
  ('Boston College', 'ACC', 11, 20),
  ('Georgia Tech', 'ACC', 11, 20);

SET CONSTRAINTS ALL IMMEDIATE;
COMMIT;