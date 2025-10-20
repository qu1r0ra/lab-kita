"""
Database Configuration for Flight Data Warehouse ETL
Update these values with your actual database credentials
"""

# Database Configuration
DB_CONFIG = {
    'source': {
        'host': 'localhost',
        'user': 'root', 
        'password': 'password',  # Change to your MySQL password
        'database': 'source_data',
        'port': 3306,
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    },
    'warehouse': {
        'host': 'localhost',
        'user': 'root',
        'password': 'password',  # Change to your MySQL password
        'database': 'flight_warehouse',
        'port': 3306,
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
}

# File Paths Configuration
DATA_PATHS = {
    'flights': 'data/airlines_flights_data.csv',
    'weather_mumbai': 'data/Historical Weather Data/Mumbai/',
    'weather_delhi': 'data/Historical Weather Data/New Delhi/',
    'complaints': 'data/Passenger Complaints/',
    'forecast': 'data/flight ticket forecast/'
}

# ETL Settings
ETL_SETTINGS = {
    'batch_size': 1000,  # Number of records to process in each batch
    'max_workers': 4,    # Number of parallel workers for processing
    'log_level': 'INFO'  # DEBUG, INFO, WARNING, ERROR
}

# Weather API Configuration (if using live data)
WEATHER_CONFIG = {
    'open_meteo_url': 'https://archive-api.open-meteo.com/v1/archive',
    'locations': {
        'Mumbai': {'lat': 19.0760, 'lon': 72.8777},
        'New Delhi': {'lat': 28.7041, 'lon': 77.1025}
    }
}

# Data Processing Settings
PROCESSING_CONFIG = {
    'default_numeric_value': 0,
    'default_text_value': 'Unknown',
    'date_format': '%Y-%m-%d',
    'datetime_format': '%Y-%m-%d %H:%M:%S'
}

# Column Mappings for Different Datasets
COLUMN_MAPPINGS = {
    'flights': {
        # Map source column names to standard names
        'airline': 'airline',
        'flight_code': 'flight_code', 
        'source_city': 'source_city',
        'destination_city': 'destination_city',
        'departure_time': 'departure_time',
        'arrival_time': 'arrival_time',
        'duration': 'duration',
        'price': 'price',
        'stops': 'stops',
        'class': 'class',
        'days_left': 'days_left'
    },
    'weather': {
        'temperature_2m': 'temperature',
        'relative_humidity_2m': 'relative_humidity', 
        'precipitation': 'precipitation',
        'rain': 'rain',
        'cloud_cover': 'cloud_cover',
        'wind_speed_10m': 'wind_speed',
        'wind_direction_10m': 'wind_direction',
        'wind_gusts_10m': 'wind_gusts',
        'pressure_msl': 'pressure_msl',
        'weather_code': 'weather_code'
    }
}

# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'etl.log',
            'formatter': 'standard'
        }
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}