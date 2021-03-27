CREATE TABLE public.component_individual_inputs (
	tweet_input varchar NULL,
	news_input varchar NULL,
	stock_input varchar NULL,
	uuid varchar NULL
);
CREATE TABLE public.entity_params (
	id varchar NOT NULL,
	"type" varchar NOT NULL,
	"key" varchar NOT NULL,
	value varchar NOT NULL,
	CONSTRAINT entity_params_pk PRIMARY KEY (id, type, key, value)
);
CREATE TABLE public.input_requests (
	id varchar NOT NULL,
	inputstr varchar NOT NULL,
	"time" timestamp NOT NULL,
	responsestr varchar NOT NULL,
	CONSTRAINT input_requests_pk PRIMARY KEY (id, inputstr, "time", responsestr)
);
CREATE TABLE public.news_complete (
	uuid varchar NULL,
	news_response_complete varchar NULL
);
CREATE TABLE public.news_individual (
	uuid varchar NULL,
	status_text_processed varchar NULL,
	sentiment_value varchar NULL,
	url varchar NULL
);
CREATE TABLE public.stock_complete_response (
	uuid varchar NULL,
	stock_complete_response varchar NULL
);
CREATE TABLE public.stock_historical_data (
	function_type varchar NULL,
	data_type varchar NULL,
	value varchar NULL,
	"timestamp" varchar NULL,
	symbol_name varchar NULL
);
CREATE TABLE public.stock_predicted_data (
	uuid varchar NULL,
	"timestamp" varchar NULL,
	value varchar NULL,
	function_type varchar NULL,
	data_type varchar NULL,
	symbol_name varchar NULL
);
CREATE TABLE public.system_params (
	"type" varchar NOT NULL,
	"key" varchar NOT NULL,
	value varchar NOT NULL,
	CONSTRAINT system_params_pk PRIMARY KEY (type, key, value)
);
CREATE TABLE public.tweet_complete (
	uuid varchar NULL,
	tweet_text varchar NULL
);
CREATE TABLE public.tweet_individual (
	uuid varchar NULL,
	status_text_processed varchar NULL,
	sentiment_value varchar NULL,
	tweet_id varchar NULL
);
