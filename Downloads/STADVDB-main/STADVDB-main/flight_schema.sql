-- ============================================
-- STAR SCHEMA: FLIGHTS
-- India Flight Data + UK Passenger Complaint Data + Mumbai/New Delhi Weather
-- ============================================
-- ============================================
-- DIMENSION TABLES
-- ============================================
CREATE TABLE dim_airline (
    airline_key INT PRIMARY KEY,
    airline_name VARCHAR(200)
);

CREATE TABLE dim_route (
    route_key INT PRIMARY KEY,
    origin_city VARCHAR(50),
    destination_city VARCHAR(50)
);

CREATE TABLE dim_flight (
    flight_key INT PRIMARY KEY,
    flight_code VARCHAR(10),
    flight_class VARCHAR(50),
	departure_time VARCHAR(50), --
    arrival_time VARCHAR(50) -- 

);

-- ============================================
-- FACT TABLES
-- ============================================
CREATE TABLE fact_flight_metrics (
    flight_metric_key BIGINT PRIMARY KEY,
    flight_key INT,
    airline_key INT,
    route_key INT,
    flight_stops INT,
    flight_duration FLOAT, -- in hours
    flight_price INT,
    days_left INT, -- days left until flight
    
    FOREIGN KEY (flight_key) REFERENCES dim_flight(flight_key),
    FOREIGN KEY (airline_key) REFERENCES dim_airline(airline_key),
    FOREIGN KEY (route_key) REFERENCES dim_route(route_key)
);

CREATE TABLE fact_weather_metrics (
    weather_metric_key BIGINT PRIMARY KEY,
    location VARCHAR(50), -- Mumbai or New Delhi
    temperature FLOAT, -- celcius
    relative_humidity INT, -- 2m, %
    precipitation INT, -- mm
    rain INT, -- mm
    cloud_cover INT, -- %
    wind_speed FLOAT, -- 10m, %
    wind_direction INT, -- 10m, °
    wind_gusts FLOAT, -- 10m, km/h
    pressure_msl INT, -- hPa
    weather_code INT, -- wmocode
    is_day BOOL
);

CREATE TABLE fact_route_metrics (
    route_metric_key INT PRIMARY KEY,
    route_key INT,
    route_duration INT,
    route_distance INT,
    route_stops INT,
    route_price_avg INT, -- aggregate the price for every flight on a route
    route_flight_amount INT, -- number of flights taken on a route
    
    FOREIGN KEY (route_key) REFERENCES dim_route(route_key)
);

CREATE TABLE fact_complaint_metrics (
    complaint_metric_key INT PRIMARY KEY,
    date_year INT,
    airline_key INT,
    complaints_per_million INT,
    uphold_rate INT, -- in %
    average_award_per_complaint INT, -- in GBP
    
    FOREIGN KEY (airline_key) REFERENCES dim_airline(airline_key)
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================
CREATE INDEX idx_dim_airline ON dim_airline(airline_key);
CREATE INDEX idx_dim_route ON dim_route(route_key);
CREATE INDEX idx_dim_flight ON dim_flight(flight_key);

CREATE INDEX idx_fact_flight_airline ON fact_flight_metrics(airline_key);
CREATE INDEX idx_fact_flight_route ON fact_flight_metrics(route_key);

CREATE INDEX idx_fact_weather_location ON fact_weather_metrics(location);

CREATE INDEX idx_fact_route_route ON fact_route_metrics(route_key);

CREATE INDEX idx_fact_complaint_airline ON fact_complaint_metrics(airline_key);