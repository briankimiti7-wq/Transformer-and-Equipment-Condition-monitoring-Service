-- TECM physical schema. Alembic migration 0001 is authoritative.


CREATE TABLE assessment_methodologies (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	code VARCHAR NOT NULL, 
	version VARCHAR NOT NULL, 
	assessment_type VARCHAR NOT NULL, 
	description VARCHAR NOT NULL, 
	source VARCHAR NOT NULL, 
	source_edition VARCHAR, 
	configuration JSON NOT NULL, 
	validation_status VARCHAR NOT NULL, 
	effective_from DATETIME NOT NULL, 
	effective_to DATETIME, 
	CONSTRAINT pk_assessment_methodologies PRIMARY KEY (id), 
	CONSTRAINT uq_assessment_methodologies_code_version UNIQUE (code, version), 
	CONSTRAINT ck_assessment_methodologies_0 CHECK (validation_status IN ('draft','validated','retired')), 
	CONSTRAINT ck_assessment_methodologies_1 CHECK (effective_to IS NULL OR effective_to > effective_from)
)

;



CREATE TABLE asset_types (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	code VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	description VARCHAR, 
	analytics_supported BOOLEAN NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	CONSTRAINT pk_asset_types PRIMARY KEY (id), 
	CONSTRAINT uq_asset_types_code UNIQUE (code), 
	CHECK (analytics_supported IN (0, 1)), 
	CHECK (is_active IN (0, 1))
)

;



CREATE TABLE monitoring_parameters (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	code VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	canonical_unit VARCHAR NOT NULL, 
	category VARCHAR NOT NULL, 
	applicability VARCHAR NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	CONSTRAINT pk_monitoring_parameters PRIMARY KEY (id), 
	CONSTRAINT uq_monitoring_parameters_code UNIQUE (code), 
	CHECK (is_active IN (0, 1))
)

;



CREATE TABLE organisations (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	code VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	industry VARCHAR, 
	country VARCHAR NOT NULL, 
	address VARCHAR, 
	contact_email VARCHAR, 
	contact_phone VARCHAR, 
	is_active BOOLEAN NOT NULL, 
	CONSTRAINT pk_organisations PRIMARY KEY (id), 
	CONSTRAINT uq_organisations_code UNIQUE (code), 
	CHECK (is_active IN (0, 1))
)

;



CREATE TABLE permissions (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	code VARCHAR NOT NULL, 
	description VARCHAR NOT NULL, 
	CONSTRAINT pk_permissions PRIMARY KEY (id), 
	CONSTRAINT uq_permissions_code UNIQUE (code)
)

;



CREATE TABLE roles (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	code VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	description VARCHAR, 
	CONSTRAINT pk_roles PRIMARY KEY (id), 
	CONSTRAINT uq_roles_code UNIQUE (code)
)

;



CREATE TABLE data_sources (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	code VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	source_type VARCHAR NOT NULL, 
	description VARCHAR, 
	is_active BOOLEAN NOT NULL, 
	CONSTRAINT pk_data_sources PRIMARY KEY (id), 
	CONSTRAINT fk_data_sources_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_data_sources_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT uq_data_sources_organisation_id_code UNIQUE (organisation_id, code), 
	CONSTRAINT ck_data_sources_0 CHECK (source_type IN ('manual','csv','excel','sensor','scada','simulation')), 
	CHECK (is_active IN (0, 1))
)

;



CREATE TABLE role_permissions (
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	role_id VARCHAR NOT NULL, 
	permission_id VARCHAR NOT NULL, 
	CONSTRAINT pk_role_permissions PRIMARY KEY (role_id, permission_id), 
	CONSTRAINT fk_role_permissions_role_id_roles FOREIGN KEY(role_id) REFERENCES roles (id) ON DELETE RESTRICT, 
	CONSTRAINT fk_role_permissions_permission_id_permissions FOREIGN KEY(permission_id) REFERENCES permissions (id) ON DELETE RESTRICT
)

;



CREATE TABLE substations (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	code VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	location VARCHAR NOT NULL, 
	latitude FLOAT, 
	longitude FLOAT, 
	voltage_kv FLOAT, 
	description VARCHAR, 
	status VARCHAR NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	CONSTRAINT pk_substations PRIMARY KEY (id), 
	CONSTRAINT fk_substations_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_substations_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT uq_substations_organisation_id_code UNIQUE (organisation_id, code), 
	CONSTRAINT ck_substations_0 CHECK (voltage_kv IS NULL OR voltage_kv > 0), 
	CONSTRAINT ck_substations_1 CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90), 
	CONSTRAINT ck_substations_2 CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180), 
	CHECK (is_active IN (0, 1))
)

;



CREATE TABLE users (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR, 
	role_id VARCHAR NOT NULL, 
	email VARCHAR NOT NULL, 
	display_name VARCHAR NOT NULL, 
	password_hash VARCHAR NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	is_platform_admin BOOLEAN NOT NULL, 
	failed_attempts INTEGER NOT NULL, 
	locked_until DATETIME, 
	last_login_at DATETIME, 
	CONSTRAINT pk_users PRIMARY KEY (id), 
	CONSTRAINT fk_users_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_users_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_users_role_id_roles FOREIGN KEY(role_id) REFERENCES roles (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_users_email UNIQUE (email), 
	CONSTRAINT ck_users_0 CHECK (organisation_id IS NOT NULL OR is_platform_admin = 1), 
	CONSTRAINT ck_users_1 CHECK (failed_attempts >= 0), 
	CHECK (is_active IN (0, 1)), 
	CHECK (is_platform_admin IN (0, 1))
)

;



CREATE TABLE assets (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	substation_id VARCHAR NOT NULL, 
	asset_type_id VARCHAR NOT NULL, 
	code VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	manufacturer VARCHAR, 
	model VARCHAR, 
	serial_number VARCHAR, 
	manufactured_year INTEGER, 
	installed_on DATE, 
	commissioned_on DATE, 
	status VARCHAR NOT NULL, 
	criticality VARCHAR NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	CONSTRAINT pk_assets PRIMARY KEY (id), 
	CONSTRAINT fk_assets_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_assets_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_assets_organisation_id_substation_id_substations FOREIGN KEY(organisation_id, substation_id) REFERENCES substations (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_assets_asset_type_id_asset_types FOREIGN KEY(asset_type_id) REFERENCES asset_types (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_assets_organisation_id_code UNIQUE (organisation_id, code), 
	CONSTRAINT ck_assets_0 CHECK (criticality IN ('Low','Medium','High','Critical')), 
	CHECK (is_active IN (0, 1))
)

;



CREATE TABLE audit_logs (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR, 
	actor_id VARCHAR, 
	action VARCHAR NOT NULL, 
	entity_type VARCHAR NOT NULL, 
	entity_id VARCHAR, 
	occurred_at DATETIME NOT NULL, 
	details JSON NOT NULL, 
	request_id VARCHAR, 
	CONSTRAINT pk_audit_logs PRIMARY KEY (id), 
	CONSTRAINT fk_audit_logs_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_audit_logs_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_audit_logs_organisation_id_actor_id_users FOREIGN KEY(organisation_id, actor_id) REFERENCES users (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_audit_logs_actor_id_users FOREIGN KEY(actor_id) REFERENCES users (id) ON DELETE RESTRICT
)

;
CREATE INDEX ix_audit_logs_0 ON audit_logs (organisation_id, occurred_at);


CREATE TABLE data_import_batches (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	source_id VARCHAR NOT NULL, 
	uploaded_by VARCHAR NOT NULL, 
	filename VARCHAR NOT NULL, 
	file_sha256 VARCHAR NOT NULL, 
	stored_path VARCHAR, 
	status VARCHAR NOT NULL, 
	total_rows INTEGER NOT NULL, 
	accepted_rows INTEGER NOT NULL, 
	rejected_rows INTEGER NOT NULL, 
	duplicate_rows INTEGER NOT NULL, 
	mapping_snapshot JSON NOT NULL, 
	confirmed_at DATETIME, 
	CONSTRAINT pk_data_import_batches PRIMARY KEY (id), 
	CONSTRAINT fk_data_import_batches_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_data_import_batches_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_data_import_batches_organisation_id_source_id_data_sources FOREIGN KEY(organisation_id, source_id) REFERENCES data_sources (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_data_import_batches_organisation_id_uploaded_by_users FOREIGN KEY(organisation_id, uploaded_by) REFERENCES users (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT uq_data_import_batches_organisation_id_id_source_id UNIQUE (organisation_id, id, source_id), 
	CONSTRAINT ck_data_import_batches_0 CHECK (total_rows >= 0 AND accepted_rows >= 0 AND rejected_rows >= 0 AND duplicate_rows >= 0), 
	CONSTRAINT ck_data_import_batches_1 CHECK (status IN ('preview','validated','importing','completed','failed')), 
	CONSTRAINT ck_data_import_batches_2 CHECK (status != 'completed' OR total_rows = accepted_rows + rejected_rows + duplicate_rows)
)

;



CREATE TABLE dga_samples (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	asset_id VARCHAR NOT NULL, 
	source_id VARCHAR NOT NULL, 
	batch_id VARCHAR, 
	recorded_by VARCHAR, 
	sample_reference VARCHAR NOT NULL, 
	sampled_at DATETIME NOT NULL, 
	laboratory VARCHAR, 
	method VARCHAR, 
	notes VARCHAR, 
	is_simulated BOOLEAN NOT NULL, 
	CONSTRAINT pk_dga_samples PRIMARY KEY (id), 
	CONSTRAINT fk_dga_samples_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_dga_samples_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_dga_samples_organisation_id_asset_id_assets FOREIGN KEY(organisation_id, asset_id) REFERENCES assets (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_dga_samples_organisation_id_source_id_data_sources FOREIGN KEY(organisation_id, source_id) REFERENCES data_sources (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_dga_samples_organisation_id_batch_id_data_import_batches FOREIGN KEY(organisation_id, batch_id) REFERENCES data_import_batches (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_dga_samples_organisation_id_recorded_by_users FOREIGN KEY(organisation_id, recorded_by) REFERENCES users (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT uq_dga_samples_organisation_id_asset_id_sample_reference UNIQUE (organisation_id, asset_id, sample_reference), 
	CONSTRAINT uq_dga_samples_organisation_id_id_asset_id UNIQUE (organisation_id, id, asset_id), 
	CHECK (is_simulated IN (0, 1))
)

;
CREATE INDEX ix_dga_samples_0 ON dga_samples (organisation_id, asset_id, sampled_at);


CREATE TABLE import_row_errors (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	batch_id VARCHAR NOT NULL, 
	row_number INTEGER NOT NULL, 
	column_name VARCHAR, 
	error_code VARCHAR NOT NULL, 
	message VARCHAR NOT NULL, 
	raw_row JSON NOT NULL, 
	CONSTRAINT pk_import_row_errors PRIMARY KEY (id), 
	CONSTRAINT fk_import_row_errors_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_import_row_errors_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_import_row_errors_organisation_id_batch_id_data_import_batches FOREIGN KEY(organisation_id, batch_id) REFERENCES data_import_batches (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT ck_import_row_errors_0 CHECK (row_number > 0)
)

;



CREATE TABLE parameter_limits (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	parameter_id VARCHAR NOT NULL, 
	asset_type_id VARCHAR, 
	asset_id VARCHAR, 
	regime VARCHAR NOT NULL, 
	applicability VARCHAR NOT NULL, 
	warning_low FLOAT, 
	warning_high FLOAT, 
	critical_low FLOAT, 
	critical_high FLOAT, 
	unit VARCHAR NOT NULL, 
	source VARCHAR NOT NULL, 
	source_edition VARCHAR, 
	revision VARCHAR NOT NULL, 
	effective_from DATETIME NOT NULL, 
	effective_to DATETIME, 
	approved_by VARCHAR NOT NULL, 
	is_demo BOOLEAN NOT NULL, 
	CONSTRAINT pk_parameter_limits PRIMARY KEY (id), 
	CONSTRAINT fk_parameter_limits_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_parameter_limits_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_parameter_limits_parameter_id_monitoring_parameters FOREIGN KEY(parameter_id) REFERENCES monitoring_parameters (id) ON DELETE RESTRICT, 
	CONSTRAINT fk_parameter_limits_asset_type_id_asset_types FOREIGN KEY(asset_type_id) REFERENCES asset_types (id) ON DELETE RESTRICT, 
	CONSTRAINT fk_parameter_limits_organisation_id_asset_id_assets FOREIGN KEY(organisation_id, asset_id) REFERENCES assets (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_parameter_limits_organisation_id_approved_by_users FOREIGN KEY(organisation_id, approved_by) REFERENCES users (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT ck_parameter_limits_0 CHECK (warning_low IS NOT NULL OR warning_high IS NOT NULL OR critical_low IS NOT NULL OR critical_high IS NOT NULL), 
	CONSTRAINT ck_parameter_limits_1 CHECK (effective_to IS NULL OR effective_to > effective_from), 
	CONSTRAINT ck_parameter_limits_2 CHECK (critical_low IS NULL OR warning_low IS NULL OR critical_low <= warning_low), 
	CONSTRAINT ck_parameter_limits_3 CHECK (warning_high IS NULL OR critical_high IS NULL OR warning_high <= critical_high), 
	CONSTRAINT ck_parameter_limits_4 CHECK (warning_low IS NULL OR warning_high IS NULL OR warning_low < warning_high), 
	CHECK (is_demo IN (0, 1))
)

;



CREATE TABLE prediction_records (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	asset_id VARCHAR NOT NULL, 
	parameter_id VARCHAR, 
	methodology_id VARCHAR NOT NULL, 
	analysis_type VARCHAR NOT NULL, 
	window_start DATETIME NOT NULL, 
	window_end DATETIME NOT NULL, 
	generated_at DATETIME NOT NULL, 
	horizon_hours FLOAT, 
	output_snapshot JSON NOT NULL, 
	limitations VARCHAR NOT NULL, 
	is_simulated BOOLEAN NOT NULL, 
	CONSTRAINT pk_prediction_records PRIMARY KEY (id), 
	CONSTRAINT fk_prediction_records_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_prediction_records_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_prediction_records_organisation_id_asset_id_assets FOREIGN KEY(organisation_id, asset_id) REFERENCES assets (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_prediction_records_parameter_id_monitoring_parameters FOREIGN KEY(parameter_id) REFERENCES monitoring_parameters (id) ON DELETE RESTRICT, 
	CONSTRAINT fk_prediction_records_methodology_id_assessment_methodologies FOREIGN KEY(methodology_id) REFERENCES assessment_methodologies (id) ON DELETE RESTRICT, 
	CONSTRAINT ck_prediction_records_0 CHECK (window_end >= window_start), 
	CHECK (is_simulated IN (0, 1))
)

;



CREATE TABLE relay_events (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	asset_id VARCHAR NOT NULL, 
	source_id VARCHAR NOT NULL, 
	batch_id VARCHAR, 
	occurred_at DATETIME NOT NULL, 
	recorded_at DATETIME NOT NULL, 
	protection_function VARCHAR NOT NULL, 
	event_type VARCHAR NOT NULL, 
	breaker_state VARCHAR, 
	phase VARCHAR, 
	value FLOAT, 
	unit VARCHAR, 
	evidence_snapshot JSON NOT NULL, 
	external_record_id VARCHAR, 
	is_simulated BOOLEAN NOT NULL, 
	CONSTRAINT pk_relay_events PRIMARY KEY (id), 
	CONSTRAINT fk_relay_events_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_relay_events_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_relay_events_organisation_id_asset_id_assets FOREIGN KEY(organisation_id, asset_id) REFERENCES assets (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_relay_events_organisation_id_source_id_data_sources FOREIGN KEY(organisation_id, source_id) REFERENCES data_sources (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_relay_events_organisation_id_batch_id_data_import_batches FOREIGN KEY(organisation_id, batch_id) REFERENCES data_import_batches (organisation_id, id) ON DELETE RESTRICT, 
	CHECK (is_simulated IN (0, 1))
)

;
CREATE INDEX ix_relay_events_0 ON relay_events (organisation_id, asset_id, occurred_at);


CREATE TABLE reports (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	asset_id VARCHAR, 
	substation_id VARCHAR, 
	created_by VARCHAR NOT NULL, 
	report_type VARCHAR NOT NULL, 
	format VARCHAR NOT NULL, 
	period_start DATETIME, 
	period_end DATETIME, 
	status VARCHAR NOT NULL, 
	file_path VARCHAR, 
	file_sha256 VARCHAR, 
	scope_snapshot JSON NOT NULL, 
	generated_at DATETIME, 
	CONSTRAINT pk_reports PRIMARY KEY (id), 
	CONSTRAINT fk_reports_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_reports_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_reports_organisation_id_asset_id_assets FOREIGN KEY(organisation_id, asset_id) REFERENCES assets (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_reports_organisation_id_substation_id_substations FOREIGN KEY(organisation_id, substation_id) REFERENCES substations (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_reports_organisation_id_created_by_users FOREIGN KEY(organisation_id, created_by) REFERENCES users (organisation_id, id) ON DELETE RESTRICT
)

;



CREATE TABLE sensors (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	asset_id VARCHAR NOT NULL, 
	parameter_id VARCHAR NOT NULL, 
	code VARCHAR NOT NULL, 
	manufacturer VARCHAR, 
	model VARCHAR, 
	serial_number VARCHAR, 
	protocol VARCHAR, 
	installed_at DATETIME, 
	communication_status VARCHAR NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	CONSTRAINT pk_sensors PRIMARY KEY (id), 
	CONSTRAINT fk_sensors_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_sensors_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_sensors_organisation_id_asset_id_assets FOREIGN KEY(organisation_id, asset_id) REFERENCES assets (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_sensors_parameter_id_monitoring_parameters FOREIGN KEY(parameter_id) REFERENCES monitoring_parameters (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_sensors_organisation_id_code UNIQUE (organisation_id, code), 
	CONSTRAINT uq_sensors_organisation_id_id_asset_id_parameter_id UNIQUE (organisation_id, id, asset_id, parameter_id), 
	CHECK (is_active IN (0, 1))
)

;



CREATE TABLE transformer_details (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	asset_id VARCHAR NOT NULL, 
	application VARCHAR NOT NULL, 
	construction VARCHAR NOT NULL, 
	rating_kva FLOAT NOT NULL, 
	primary_kv FLOAT NOT NULL, 
	secondary_kv FLOAT NOT NULL, 
	phases INTEGER NOT NULL, 
	frequency_hz FLOAT NOT NULL, 
	vector_group VARCHAR, 
	cooling VARCHAR, 
	insulation_class VARCHAR, 
	impedance_percent FLOAT, 
	tap_changer_type VARCHAR, 
	rated_primary_a FLOAT, 
	rated_secondary_a FLOAT, 
	oil_volume_l FLOAT, 
	CONSTRAINT pk_transformer_details PRIMARY KEY (id), 
	CONSTRAINT fk_transformer_details_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_transformer_details_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_transformer_details_organisation_id_asset_id_assets FOREIGN KEY(organisation_id, asset_id) REFERENCES assets (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT uq_transformer_details_asset_id UNIQUE (asset_id), 
	CONSTRAINT ck_transformer_details_0 CHECK (application IN ('power','distribution')), 
	CONSTRAINT ck_transformer_details_1 CHECK (construction IN ('oil','dry')), 
	CONSTRAINT ck_transformer_details_2 CHECK (rating_kva > 0 AND primary_kv > 0 AND secondary_kv > 0 AND frequency_hz > 0), 
	CONSTRAINT ck_transformer_details_3 CHECK (phases IN (1,3)), 
	CONSTRAINT ck_transformer_details_4 CHECK (construction != 'dry' OR oil_volume_l IS NULL), 
	CONSTRAINT ck_transformer_details_5 CHECK (oil_volume_l IS NULL OR oil_volume_l >= 0)
)

;



CREATE TABLE work_orders (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	asset_id VARCHAR NOT NULL, 
	code VARCHAR NOT NULL, 
	title VARCHAR NOT NULL, 
	description VARCHAR NOT NULL, 
	priority VARCHAR NOT NULL, 
	status VARCHAR NOT NULL, 
	assigned_to VARCHAR, 
	created_by VARCHAR NOT NULL, 
	due_on DATE, 
	started_at DATETIME, 
	completed_at DATETIME, 
	cancelled_at DATETIME, 
	cancellation_reason VARCHAR, 
	CONSTRAINT pk_work_orders PRIMARY KEY (id), 
	CONSTRAINT fk_work_orders_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_work_orders_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_work_orders_organisation_id_asset_id_assets FOREIGN KEY(organisation_id, asset_id) REFERENCES assets (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_work_orders_organisation_id_assigned_to_users FOREIGN KEY(organisation_id, assigned_to) REFERENCES users (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_work_orders_organisation_id_created_by_users FOREIGN KEY(organisation_id, created_by) REFERENCES users (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT uq_work_orders_organisation_id_code UNIQUE (organisation_id, code), 
	CONSTRAINT uq_work_orders_organisation_id_id_asset_id UNIQUE (organisation_id, id, asset_id), 
	CONSTRAINT ck_work_orders_0 CHECK (status IN ('Open','Assigned','In Progress','Completed','Cancelled')), 
	CONSTRAINT ck_work_orders_1 CHECK (status != 'Completed' OR completed_at IS NOT NULL), 
	CONSTRAINT ck_work_orders_2 CHECK (status != 'Cancelled' OR cancellation_reason IS NOT NULL)
)

;
CREATE INDEX ix_work_orders_0 ON work_orders (organisation_id, status, due_on);


CREATE TABLE condition_assessments (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	asset_id VARCHAR NOT NULL, 
	methodology_id VARCHAR NOT NULL, 
	sample_id VARCHAR, 
	assessment_type VARCHAR NOT NULL, 
	assessed_at DATETIME NOT NULL, 
	assessed_by VARCHAR, 
	result_status VARCHAR NOT NULL, 
	evidence_snapshot JSON NOT NULL, 
	limitations VARCHAR, 
	recommendations VARCHAR, 
	CONSTRAINT pk_condition_assessments PRIMARY KEY (id), 
	CONSTRAINT fk_condition_assessments_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_condition_assessments_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_condition_assessments_organisation_id_asset_id_assets FOREIGN KEY(organisation_id, asset_id) REFERENCES assets (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_condition_assessments_methodology_id_assessment_methodologies FOREIGN KEY(methodology_id) REFERENCES assessment_methodologies (id) ON DELETE RESTRICT, 
	CONSTRAINT fk_condition_assessments_organisation_id_sample_id_dga_samples FOREIGN KEY(organisation_id, sample_id) REFERENCES dga_samples (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_condition_assessments_organisation_id_assessed_by_users FOREIGN KEY(organisation_id, assessed_by) REFERENCES users (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT uq_condition_assessments_organisation_id_id_asset_id UNIQUE (organisation_id, id, asset_id), 
	CONSTRAINT fk_condition_assessments_organisation_id_sample_id_asset_id_dga_samples FOREIGN KEY(organisation_id, sample_id, asset_id) REFERENCES dga_samples (organisation_id, id, asset_id) ON DELETE RESTRICT
)

;



CREATE TABLE dga_gas_measurements (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	sample_id VARCHAR NOT NULL, 
	gas_code VARCHAR NOT NULL, 
	concentration_ppm FLOAT, 
	qualifier VARCHAR NOT NULL, 
	detection_limit_ppm FLOAT, 
	quality VARCHAR NOT NULL, 
	CONSTRAINT pk_dga_gas_measurements PRIMARY KEY (id), 
	CONSTRAINT fk_dga_gas_measurements_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_dga_gas_measurements_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_dga_gas_measurements_organisation_id_sample_id_dga_samples FOREIGN KEY(organisation_id, sample_id) REFERENCES dga_samples (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT uq_dga_gas_measurements_sample_id_gas_code UNIQUE (sample_id, gas_code), 
	CONSTRAINT ck_dga_gas_measurements_0 CHECK (gas_code IN ('H2','CH4','C2H6','C2H4','C2H2','CO','CO2')), 
	CONSTRAINT ck_dga_gas_measurements_1 CHECK (qualifier IN ('measured','below_limit','not_measured')), 
	CONSTRAINT ck_dga_gas_measurements_2 CHECK (concentration_ppm IS NULL OR concentration_ppm >= 0), 
	CONSTRAINT ck_dga_gas_measurements_3 CHECK (detection_limit_ppm IS NULL OR detection_limit_ppm >= 0), 
	CONSTRAINT ck_dga_gas_measurements_4 CHECK (qualifier != 'measured' OR concentration_ppm IS NOT NULL), 
	CONSTRAINT ck_dga_gas_measurements_5 CHECK (qualifier != 'below_limit' OR detection_limit_ppm IS NOT NULL)
)

;



CREATE TABLE inspection_records (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	asset_id VARCHAR NOT NULL, 
	work_order_id VARCHAR, 
	inspector_id VARCHAR, 
	inspected_at DATETIME NOT NULL, 
	inspection_type VARCHAR NOT NULL, 
	findings VARCHAR NOT NULL, 
	checklist_snapshot JSON NOT NULL, 
	recommendations VARCHAR, 
	external_reference VARCHAR, 
	CONSTRAINT pk_inspection_records PRIMARY KEY (id), 
	CONSTRAINT fk_inspection_records_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_inspection_records_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_inspection_records_organisation_id_asset_id_assets FOREIGN KEY(organisation_id, asset_id) REFERENCES assets (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_inspection_records_organisation_id_work_order_id_work_orders FOREIGN KEY(organisation_id, work_order_id) REFERENCES work_orders (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_inspection_records_organisation_id_inspector_id_users FOREIGN KEY(organisation_id, inspector_id) REFERENCES users (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_inspection_records_organisation_id_work_order_id_asset_id_work_orders FOREIGN KEY(organisation_id, work_order_id, asset_id) REFERENCES work_orders (organisation_id, id, asset_id) ON DELETE RESTRICT
)

;



CREATE TABLE maintenance_records (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	asset_id VARCHAR NOT NULL, 
	work_order_id VARCHAR, 
	performed_by VARCHAR, 
	performed_at DATETIME NOT NULL, 
	activity_type VARCHAR NOT NULL, 
	findings VARCHAR NOT NULL, 
	actions_taken VARCHAR NOT NULL, 
	replaced_components VARCHAR, 
	next_due_on DATE, 
	source_reference VARCHAR, 
	CONSTRAINT pk_maintenance_records PRIMARY KEY (id), 
	CONSTRAINT fk_maintenance_records_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_maintenance_records_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_maintenance_records_organisation_id_asset_id_assets FOREIGN KEY(organisation_id, asset_id) REFERENCES assets (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_maintenance_records_organisation_id_work_order_id_work_orders FOREIGN KEY(organisation_id, work_order_id) REFERENCES work_orders (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_maintenance_records_organisation_id_performed_by_users FOREIGN KEY(organisation_id, performed_by) REFERENCES users (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_maintenance_records_organisation_id_work_order_id_asset_id_work_orders FOREIGN KEY(organisation_id, work_order_id, asset_id) REFERENCES work_orders (organisation_id, id, asset_id) ON DELETE RESTRICT
)

;



CREATE TABLE measurements (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	asset_id VARCHAR NOT NULL, 
	parameter_id VARCHAR NOT NULL, 
	source_id VARCHAR NOT NULL, 
	sensor_id VARCHAR, 
	batch_id VARCHAR, 
	recorded_by VARCHAR, 
	observed_at DATETIME NOT NULL, 
	recorded_at DATETIME NOT NULL, 
	value FLOAT NOT NULL, 
	unit VARCHAR NOT NULL, 
	raw_value FLOAT NOT NULL, 
	raw_unit VARCHAR NOT NULL, 
	quality VARCHAR NOT NULL, 
	is_simulated BOOLEAN NOT NULL, 
	external_record_id VARCHAR, 
	dedupe_key VARCHAR NOT NULL, 
	supersedes_id VARCHAR, 
	CONSTRAINT pk_measurements PRIMARY KEY (id), 
	CONSTRAINT fk_measurements_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_measurements_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_measurements_organisation_id_asset_id_assets FOREIGN KEY(organisation_id, asset_id) REFERENCES assets (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_measurements_parameter_id_monitoring_parameters FOREIGN KEY(parameter_id) REFERENCES monitoring_parameters (id) ON DELETE RESTRICT, 
	CONSTRAINT fk_measurements_organisation_id_source_id_data_sources FOREIGN KEY(organisation_id, source_id) REFERENCES data_sources (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_measurements_organisation_id_sensor_id_sensors FOREIGN KEY(organisation_id, sensor_id) REFERENCES sensors (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_measurements_organisation_id_batch_id_data_import_batches FOREIGN KEY(organisation_id, batch_id) REFERENCES data_import_batches (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_measurements_organisation_id_recorded_by_users FOREIGN KEY(organisation_id, recorded_by) REFERENCES users (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_measurements_organisation_id_supersedes_id_measurements FOREIGN KEY(organisation_id, supersedes_id) REFERENCES measurements (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT uq_measurements_organisation_id_dedupe_key UNIQUE (organisation_id, dedupe_key), 
	CONSTRAINT uq_measurements_organisation_id_id_asset_id_parameter_id UNIQUE (organisation_id, id, asset_id, parameter_id), 
	CONSTRAINT fk_measurements_organisation_id_sensor_id_asset_id_parameter_id_sensors FOREIGN KEY(organisation_id, sensor_id, asset_id, parameter_id) REFERENCES sensors (organisation_id, id, asset_id, parameter_id) ON DELETE RESTRICT, 
	CONSTRAINT fk_measurements_organisation_id_batch_id_source_id_data_import_batches FOREIGN KEY(organisation_id, batch_id, source_id) REFERENCES data_import_batches (organisation_id, id, source_id) ON DELETE RESTRICT, 
	CHECK (is_simulated IN (0, 1))
)

;
CREATE INDEX ix_measurements_1 ON measurements (organisation_id, batch_id);
CREATE INDEX ix_measurements_0 ON measurements (organisation_id, asset_id, parameter_id, observed_at);


CREATE TABLE assessment_findings (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	assessment_id VARCHAR NOT NULL, 
	category VARCHAR NOT NULL, 
	severity VARCHAR NOT NULL, 
	statement VARCHAR NOT NULL, 
	evidence_snapshot JSON NOT NULL, 
	recommended_action VARCHAR, 
	CONSTRAINT pk_assessment_findings PRIMARY KEY (id), 
	CONSTRAINT fk_assessment_findings_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_assessment_findings_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_assessment_findings_organisation_id_assessment_id_condition_assessments FOREIGN KEY(organisation_id, assessment_id) REFERENCES condition_assessments (organisation_id, id) ON DELETE RESTRICT
)

;



CREATE TABLE fault_records (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	asset_id VARCHAR NOT NULL, 
	assessment_id VARCHAR, 
	category VARCHAR NOT NULL, 
	severity VARCHAR NOT NULL, 
	status VARCHAR NOT NULL, 
	detected_at DATETIME NOT NULL, 
	detection_method VARCHAR NOT NULL, 
	evidence_snapshot JSON NOT NULL, 
	recommended_action VARCHAR, 
	confirmed_by VARCHAR, 
	confirmed_at DATETIME, 
	resolved_at DATETIME, 
	resolution_note VARCHAR, 
	CONSTRAINT pk_fault_records PRIMARY KEY (id), 
	CONSTRAINT fk_fault_records_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_fault_records_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_fault_records_organisation_id_asset_id_assets FOREIGN KEY(organisation_id, asset_id) REFERENCES assets (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_fault_records_organisation_id_assessment_id_condition_assessments FOREIGN KEY(organisation_id, assessment_id) REFERENCES condition_assessments (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_fault_records_organisation_id_confirmed_by_users FOREIGN KEY(organisation_id, confirmed_by) REFERENCES users (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT ck_fault_records_0 CHECK (status IN ('indication','confirmed','ruled_out','resolved')), 
	CONSTRAINT ck_fault_records_1 CHECK (status != 'confirmed' OR (confirmed_by IS NOT NULL AND confirmed_at IS NOT NULL)), 
	CONSTRAINT fk_fault_records_organisation_id_assessment_id_asset_id_condition_assessments FOREIGN KEY(organisation_id, assessment_id, asset_id) REFERENCES condition_assessments (organisation_id, id, asset_id) ON DELETE RESTRICT
)

;



CREATE TABLE health_indices (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	asset_id VARCHAR NOT NULL, 
	assessment_id VARCHAR NOT NULL, 
	methodology_id VARCHAR NOT NULL, 
	calculated_at DATETIME NOT NULL, 
	score FLOAT, 
	classification VARCHAR NOT NULL, 
	completeness FLOAT NOT NULL, 
	confidence_label VARCHAR NOT NULL, 
	calculation_snapshot JSON NOT NULL, 
	CONSTRAINT pk_health_indices PRIMARY KEY (id), 
	CONSTRAINT fk_health_indices_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_health_indices_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_health_indices_organisation_id_asset_id_assets FOREIGN KEY(organisation_id, asset_id) REFERENCES assets (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_health_indices_organisation_id_assessment_id_condition_assessments FOREIGN KEY(organisation_id, assessment_id) REFERENCES condition_assessments (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_health_indices_methodology_id_assessment_methodologies FOREIGN KEY(methodology_id) REFERENCES assessment_methodologies (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_health_indices_assessment_id UNIQUE (assessment_id), 
	CONSTRAINT ck_health_indices_0 CHECK (score IS NULL OR score BETWEEN 0 AND 100), 
	CONSTRAINT ck_health_indices_1 CHECK (completeness BETWEEN 0 AND 100), 
	CONSTRAINT fk_health_indices_organisation_id_assessment_id_asset_id_condition_assessments FOREIGN KEY(organisation_id, assessment_id, asset_id) REFERENCES condition_assessments (organisation_id, id, asset_id) ON DELETE RESTRICT
)

;



CREATE TABLE alerts (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	asset_id VARCHAR NOT NULL, 
	assessment_id VARCHAR, 
	fault_id VARCHAR, 
	work_order_id VARCHAR, 
	severity VARCHAR NOT NULL, 
	title VARCHAR NOT NULL, 
	message VARCHAR NOT NULL, 
	evidence_snapshot JSON NOT NULL, 
	rule_revision VARCHAR NOT NULL, 
	dedupe_key VARCHAR NOT NULL, 
	triggered_at DATETIME NOT NULL, 
	status VARCHAR NOT NULL, 
	acknowledged_by VARCHAR, 
	acknowledged_at DATETIME, 
	resolved_by VARCHAR, 
	resolved_at DATETIME, 
	CONSTRAINT pk_alerts PRIMARY KEY (id), 
	CONSTRAINT fk_alerts_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_alerts_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_alerts_organisation_id_asset_id_assets FOREIGN KEY(organisation_id, asset_id) REFERENCES assets (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_alerts_organisation_id_assessment_id_condition_assessments FOREIGN KEY(organisation_id, assessment_id) REFERENCES condition_assessments (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_alerts_organisation_id_fault_id_fault_records FOREIGN KEY(organisation_id, fault_id) REFERENCES fault_records (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_alerts_organisation_id_work_order_id_work_orders FOREIGN KEY(organisation_id, work_order_id) REFERENCES work_orders (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_alerts_organisation_id_acknowledged_by_users FOREIGN KEY(organisation_id, acknowledged_by) REFERENCES users (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_alerts_organisation_id_resolved_by_users FOREIGN KEY(organisation_id, resolved_by) REFERENCES users (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT uq_alerts_organisation_id_dedupe_key UNIQUE (organisation_id, dedupe_key), 
	CONSTRAINT ck_alerts_0 CHECK (status IN ('open','acknowledged','resolved')), 
	CONSTRAINT ck_alerts_1 CHECK (severity IN ('Information','Warning','Critical')), 
	CONSTRAINT ck_alerts_2 CHECK (status != 'acknowledged' OR (acknowledged_by IS NOT NULL AND acknowledged_at IS NOT NULL)), 
	CONSTRAINT ck_alerts_3 CHECK (status != 'resolved' OR (resolved_by IS NOT NULL AND resolved_at IS NOT NULL))
)

;
CREATE INDEX ix_alerts_0 ON alerts (organisation_id, status, severity, triggered_at);


CREATE TABLE alert_events (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	alert_id VARCHAR NOT NULL, 
	actor_id VARCHAR NOT NULL, 
	event_type VARCHAR NOT NULL, 
	occurred_at DATETIME NOT NULL, 
	note VARCHAR, 
	outcome VARCHAR, 
	clarity_rating INTEGER, 
	idempotency_key VARCHAR NOT NULL, 
	CONSTRAINT pk_alert_events PRIMARY KEY (id), 
	CONSTRAINT fk_alert_events_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_alert_events_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_alert_events_organisation_id_alert_id_alerts FOREIGN KEY(organisation_id, alert_id) REFERENCES alerts (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_alert_events_organisation_id_actor_id_users FOREIGN KEY(organisation_id, actor_id) REFERENCES users (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT uq_alert_events_organisation_id_idempotency_key UNIQUE (organisation_id, idempotency_key), 
	CONSTRAINT ck_alert_events_0 CHECK (clarity_rating IS NULL OR clarity_rating BETWEEN 1 AND 5), 
	CONSTRAINT ck_alert_events_1 CHECK (event_type IN ('acknowledge','verify','handoff','finding','resolve','reopen','evaluate'))
)

;



CREATE TABLE notification_deliveries (
	id VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	organisation_id VARCHAR NOT NULL, 
	alert_id VARCHAR NOT NULL, 
	recipient_user_id VARCHAR NOT NULL, 
	channel VARCHAR NOT NULL, 
	status VARCHAR NOT NULL, 
	attempts INTEGER NOT NULL, 
	last_attempt_at DATETIME, 
	sent_at DATETIME, 
	error_summary VARCHAR, 
	idempotency_key VARCHAR NOT NULL, 
	CONSTRAINT pk_notification_deliveries PRIMARY KEY (id), 
	CONSTRAINT fk_notification_deliveries_organisation_id_organisations FOREIGN KEY(organisation_id) REFERENCES organisations (id) ON DELETE RESTRICT, 
	CONSTRAINT uq_notification_deliveries_organisation_id_id UNIQUE (organisation_id, id), 
	CONSTRAINT fk_notification_deliveries_organisation_id_alert_id_alerts FOREIGN KEY(organisation_id, alert_id) REFERENCES alerts (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT fk_notification_deliveries_organisation_id_recipient_user_id_users FOREIGN KEY(organisation_id, recipient_user_id) REFERENCES users (organisation_id, id) ON DELETE RESTRICT, 
	CONSTRAINT uq_notification_deliveries_organisation_id_idempotency_key UNIQUE (organisation_id, idempotency_key), 
	CONSTRAINT ck_notification_deliveries_0 CHECK (attempts >= 0), 
	CONSTRAINT ck_notification_deliveries_1 CHECK (status IN ('pending','sent','failed','cancelled'))
)

;
