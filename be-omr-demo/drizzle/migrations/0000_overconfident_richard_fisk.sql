CREATE TABLE `current_school` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`scan_id` integer NOT NULL,
	`raw_json` text NOT NULL,
	`region` text,
	`division` text,
	`school_id` text,
	`school_type` text,
	`review_required` integer DEFAULT false NOT NULL,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	FOREIGN KEY (`scan_id`) REFERENCES `omr_scan`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE INDEX `idx_curr_scan` ON `current_school` (`scan_id`);--> statement-breakpoint
CREATE INDEX `idx_curr_review` ON `current_school` (`review_required`);--> statement-breakpoint
CREATE TABLE `omr_scan` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`file_name` text,
	`file_path` text,
	`file_url` text,
	`status` text DEFAULT 'pending' NOT NULL,
	`raw_json` text NOT NULL,
	`confidence` real,
	`review_required` integer DEFAULT false NOT NULL,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL
);
--> statement-breakpoint
CREATE INDEX `idx_scan_review` ON `omr_scan` (`review_required`);--> statement-breakpoint
CREATE INDEX `idx_scan_created` ON `omr_scan` (`created_at`);--> statement-breakpoint
CREATE TABLE `previous_school` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`scan_id` integer NOT NULL,
	`raw_json` text NOT NULL,
	`school_id` text,
	`math_grade` text,
	`english_grade` text,
	`science_grade` text,
	`filipino_grade` text,
	`ap_grade` text,
	`class_size` text,
	`school_year` text,
	`review_required` integer DEFAULT false NOT NULL,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	FOREIGN KEY (`scan_id`) REFERENCES `omr_scan`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE INDEX `idx_prev_scan` ON `previous_school` (`scan_id`);--> statement-breakpoint
CREATE INDEX `idx_prev_review` ON `previous_school` (`review_required`);--> statement-breakpoint
CREATE TABLE `seed_history` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`name` text NOT NULL,
	`executed_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `seed_history_name_unique` ON `seed_history` (`name`);--> statement-breakpoint
CREATE TABLE `student_answer` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`scan_id` integer NOT NULL,
	`subject` text NOT NULL,
	`question_number` integer NOT NULL,
	`answer` text,
	`confidence` real,
	`review_required` integer DEFAULT false NOT NULL,
	`raw_json` text,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	FOREIGN KEY (`scan_id`) REFERENCES `omr_scan`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE INDEX `idx_answer_scan` ON `student_answer` (`scan_id`);--> statement-breakpoint
CREATE INDEX `idx_answer_review` ON `student_answer` (`review_required`);--> statement-breakpoint
CREATE UNIQUE INDEX `uq_scan_subject_question` ON `student_answer` (`scan_id`,`subject`,`question_number`);--> statement-breakpoint
CREATE TABLE `student` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`scan_id` integer NOT NULL,
	`raw_json` text NOT NULL,
	`last_name` text,
	`first_name` text,
	`middle_initial` text,
	`birth_month` text,
	`birth_day` text,
	`birth_year` text,
	`ssc` text,
	`four_ps` text,
	`gender` text,
	`lrn` text,
	`special_classes` text,
	`review_required` integer DEFAULT false NOT NULL,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	FOREIGN KEY (`scan_id`) REFERENCES `omr_scan`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE INDEX `idx_student_scan` ON `student` (`scan_id`);--> statement-breakpoint
CREATE INDEX `idx_student_lrn` ON `student` (`lrn`);--> statement-breakpoint
CREATE TABLE `users` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`email` text NOT NULL,
	`password_hash` text NOT NULL,
	`role` text DEFAULT 'user' NOT NULL,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `users_email_unique` ON `users` (`email`);