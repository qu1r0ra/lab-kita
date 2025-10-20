import pandas as pd
import mysql.connector
from mysql.connector import Error
import numpy as np
import os
import glob
from datetime import datetime
import config

class FlightDataETL:
    def __init__(self):
        self.source_conn = None
        self.dw_conn = None
        
    def create_connections(self):
        """Create database connections"""
        try:
            self.source_conn = mysql.connector.connect(**config.DB_CONFIG['source'])
            self.dw_conn = mysql.connector.connect(**config.DB_CONFIG['warehouse'])
            print("Database connections established successfully")
        except Error as e:
            print(f"Error connecting to database: {e}")
            raise
    
    def close_connections(self):
        """Close database connections"""
        if self.source_conn:
            self.source_conn.close()
        if self.dw_conn:
            self.dw_conn.close()
        print("Database connections closed")
    
    def extract_flight_data(self):
        """Extract from airlines_flights_data.csv"""
        print("Extracting flight data...")
        file_path = "datasets/airlines_flights_data.csv"
        
        try:
            df = pd.read_csv(file_path)
            print(f"Loaded {len(df)} rows from flight data")
            
            # Display column names to understand the structure
            print("Flight data columns:", df.columns.tolist())
            
            # Fix column name mappings
            if 'flight' in df.columns and 'flight_code' not in df.columns:
                df['flight_code'] = df['flight']
                print("✓ Mapped 'flight' column to 'flight_code'")
            
            # Handle other column name differences
            column_mappings = {
                'stops': 'flight_stops',
                'duration': 'flight_duration', 
                'price': 'flight_price'
            }
            
            for source_col, target_col in column_mappings.items():
                if source_col in df.columns:
                    df[target_col] = df[source_col]

            return df
            
        except Exception as e:
            print(f"Error reading flight data: {e}")
            return pd.DataFrame()
    
    def extract_weather_data(self):
        """Extract and combine all weather data"""
        print("Extracting weather data...")
        
        weather_data = []
        
        # Process Mumbai weather files
        mumbai_files = glob.glob("datasets/Historical Weather Data/Mumbai/*.csv")
        for file in mumbai_files:
            try:
                # Try different CSV reading options for malformed files
                df = pd.read_csv(file, on_bad_lines='skip')
                # OR try with different separator
                # df = pd.read_csv(file, sep=None, engine='python')
                df['location'] = 'Mumbai'
                weather_data.append(df)
                print(f"Loaded {len(df)} rows from {file}")
            except Exception as e:
                print(f"Error reading {file}: {e}")
                # Try alternative reading method
                try:
                    df = pd.read_csv(file, sep=None, engine='python', on_bad_lines='skip')
                    df['location'] = 'Mumbai'
                    weather_data.append(df)
                    print(f"✓ Loaded {len(df)} rows using alternative method")
                except:
                    print(f"✗ Could not read {file}")
        
        # Process New Delhi weather files  
        delhi_files = glob.glob("datasets/Historical Weather Data/New Delhi/*.csv")
        for file in delhi_files:
            try:
                df = pd.read_csv(file, on_bad_lines='skip', encoding='utf-8')
                df['location'] = 'New Delhi'
                weather_data.append(df)
                print(f"Loaded {len(df)} rows from {file}")
            except Exception as e:
                print(f"Error reading {file}: {e}")
                # Try alternative methods for Delhi files too
                try:
                    df = pd.read_csv(file, sep=';', on_bad_lines='skip')
                    df['location'] = 'New Delhi'
                    weather_data.append(df)
                    print(f"✓ Loaded {len(df)} Delhi rows using alternative method")
                except:
                    try:
                        df = pd.read_csv(file, engine='python', on_bad_lines='skip')
                        df['location'] = 'New Delhi'
                        weather_data.append(df)
                        print(f"✓ Loaded {len(df)} Delhi rows using python engine")
                    except Exception as e2:
                        print(f"✗ Could not read {file}: {e2}")
        
        if weather_data:
            combined_weather = pd.concat(weather_data, ignore_index=True)
            print(f"Combined {len(combined_weather)} total weather records")
            return combined_weather
        else:
            print("No weather data found")
            return pd.DataFrame()
    
    def extract_complaint_data(self):
        """Extract from Excel complaint files"""
        print("Extracting complaint data...")
    
        complaint_files = [
            "datasets/Passenger Complaints/Passenger Complaints Data FY23 (Q2 2022 - Q1 2023).xlsx",
            "datasets/Passenger Complaints/Passenger Complaints Data FY24 (Q2 2023 - Q1 2024).xlsx"
        ]
        
        complaint_data = []
        
        for file in complaint_files:
            if os.path.exists(file):
                try:
                    print(f"\nProcessing {os.path.basename(file)}:")
                    
                    # Read with headers in row 4 (as we identified from inspection)
                    df = pd.read_excel(file, sheet_name='Final Table', header=4)
                    
                    # Remove empty rows and columns
                    df = df.dropna(axis=1, how='all')
                    df = df.dropna(axis=0, how='all')
                    
                    # Clean column names
                    df.columns = [str(col).strip() for col in df.columns]
                    
                    print(f"  ✓ Loaded {len(df)} rows")
                    print(f"  Columns: {df.columns.tolist()}")
                    
                    # Add a source year column based on filename
                    if 'FY23' in file:
                        df['source_year'] = 2023
                    elif 'FY24' in file:
                        df['source_year'] = 2024
                    
                    complaint_data.append(df)
                    
                except Exception as e:
                    print(f"Error reading {file}: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"File not found: {file}")
        
        if complaint_data:
            combined_complaints = pd.concat(complaint_data, ignore_index=True)
            print(f"\n✓ Combined {len(combined_complaints)} total complaint records")
            return combined_complaints
        else:
            print("✗ No complaint data could be extracted")
            return pd.DataFrame()
    
    def extract_flight_forecast_data(self):
        """Extract flight forecast/training data"""
        print("Extracting flight forecast data...")
        
        try:
            # Combine training and test data
            X_train = pd.read_csv("datasets/flight ticket forecast/X_train.csv")
            y_train = pd.read_csv("datasets/flight ticket forecast/y_train.csv")
            X_test = pd.read_csv("datasets/flight ticket forecast/X_test.csv")
            y_test = pd.read_csv("datasets/flight ticket forecast/y_test.csv")
            
            # Merge features and targets
            train_data = pd.concat([X_train, y_train], axis=1)
            test_data = pd.concat([X_test, y_test], axis=1)
            
            forecast_data = pd.concat([train_data, test_data], ignore_index=True)
            print(f"Loaded {len(forecast_data)} forecast records")
            print("Forecast data columns:", forecast_data.columns.tolist())
            
            return forecast_data
            
        except Exception as e:
            print(f"Error reading forecast data: {e}")
            return pd.DataFrame()
    
    def transform_dimensions(self, df_flights):
        """Transform dimension tables from flight data"""
        print("Transforming dimension tables...")
        
        # dim_airline - extract from airline column
        if 'airline' in df_flights.columns:
            airlines = df_flights['airline'].dropna().unique()
        else:
            # Try to find airline information in other columns
            print("Warning: 'airline' column not found. Please check your flight data structure.")
            airlines = ['Unknown Airline']
        
        dim_airline = pd.DataFrame({
            'airline_key': range(1, len(airlines) + 1),
            'airline_name': airlines
        })
        
        # dim_route - extract from source and destination cities
        if all(col in df_flights.columns for col in ['source_city', 'destination_city']):
            routes = df_flights[['source_city', 'destination_city']].drop_duplicates()
        else:
            # Try alternative column names
            source_col = next((col for col in df_flights.columns if 'source' in col.lower() or 'origin' in col.lower()), 'Unknown')
            dest_col = next((col for col in df_flights.columns if 'destination' in col.lower() or 'dest' in col.lower()), 'Unknown')
            
            if source_col != 'Unknown' and dest_col != 'Unknown':
                routes = df_flights[[source_col, dest_col]].drop_duplicates()
                routes.columns = ['source_city', 'destination_city']
            else:
                routes = pd.DataFrame({'source_city': ['Unknown'], 'destination_city': ['Unknown']})
        
        dim_route = pd.DataFrame({
            'route_key': range(1, len(routes) + 1),
            'origin_city': routes['source_city'],
            'destination_city': routes['destination_city']
        })
        
        # dim_flight - extract flight details
        flight_cols = {}
        for col in ['flight_code', 'class', 'departure_time', 'arrival_time']:
            if col in df_flights.columns:
                flight_cols[col] = df_flights[col]
            else:
                # Try to find similar columns
                alt_col = next((c for c in df_flights.columns if col.split('_')[0] in c.lower()), 'Unknown')
                flight_cols[col] = df_flights.get(alt_col, 'Unknown')
        
        flight_data = pd.DataFrame(flight_cols).drop_duplicates()
        dim_flight = pd.DataFrame({
            'flight_key': range(1, len(flight_data) + 1),
            'flight_code': flight_data.get('flight_code', 'Unknown'),
            'flight_class': flight_data.get('class', 'Unknown'),
            'departure_time': flight_data.get('departure_time', 'Unknown'),
            'arrival_time': flight_data.get('arrival_time', 'Unknown')
        })
        
        print(f"Created dimensions: {len(dim_airline)} airlines, {len(dim_route)} routes, {len(dim_flight)} flights")
        return dim_airline, dim_route, dim_flight
    
    def transform_fact_flight_metrics(self, df_flights, dim_airline, dim_route, dim_flight):
        """Transform flight facts with surrogate key lookups"""
        print("Transforming flight metrics...")
        
        # Merge with dimensions to get surrogate keys
        df_fact = df_flights.merge(
            dim_airline, left_on='airline', right_on='airline_name', how='left'
        )
        
        # Merge with route dimension
        if all(col in df_flights.columns for col in ['source_city', 'destination_city']):
            df_fact = df_fact.merge(
                dim_route,
                left_on=['source_city', 'destination_city'],
                right_on=['origin_city', 'destination_city'],
                how='left'
            )
        
        # Merge with flight dimension
        if 'flight_code' in df_flights.columns and 'class' in df_flights.columns:
            df_fact = df_fact.merge(
                dim_flight,
                left_on=['flight_code', 'class'],
                right_on=['flight_code', 'flight_class'],
                how='left'
            )
        
        # Map numeric columns with proper data types
        numeric_mapping = {
            'stops': 'flight_stops',
            'duration': 'flight_duration', 
            'price': 'flight_price',
            'days_left': 'days_left'
        }
        
        for source_col, target_col in numeric_mapping.items():
            if source_col in df_fact.columns:
                df_fact[target_col] = pd.to_numeric(df_fact[source_col], errors='coerce').fillna(0)
            else:
                df_fact[target_col] = 0
        
        # Create primary key
        df_fact['flight_metric_key'] = range(1, len(df_fact) + 1)
        
        # Select final columns for fact table
        result_cols = [
            'flight_metric_key', 'flight_key', 'airline_key', 'route_key',
            'flight_stops', 'flight_duration', 'flight_price', 'days_left'
        ]
        
        # Ensure all required foreign key columns exist
        for col in ['flight_key', 'airline_key', 'route_key']:
            if col not in df_fact.columns:
                df_fact[col] = 1  # Default to first key if missing
        
        print(f"Transformed {len(df_fact)} flight metric records")
        
        # Return only the columns needed for the fact table
        return df_fact[result_cols]

    def transform_weather_data(self, df_weather):
        """Transform weather data to match schema"""
        if df_weather.empty:
            return pd.DataFrame()
            
        print("Transforming weather data...")
        
        # Map common weather column names to your schema
        column_mapping = {
            # Temperature
            'temperature_2m': 'temperature', 'temp_c': 'temperature', 'temperature': 'temperature',
            # Humidity  
            'relative_humidity_2m': 'relative_humidity', 'humidity': 'relative_humidity',
            # Precipitation
            'precipitation': 'precipitation', 'precip': 'precipitation',
            # Rain
            'rain': 'rain', 
            # Cloud cover
            'cloud_cover': 'cloud_cover', 'clouds': 'cloud_cover',
            # Wind
            'wind_speed_10m': 'wind_speed', 'wind_speed': 'wind_speed',
            'wind_direction_10m': 'wind_direction', 'wind_deg': 'wind_direction',
            'wind_gusts_10m': 'wind_gusts', 'wind_gust': 'wind_gusts',
            # Pressure
            'pressure_msl': 'pressure_msl', 'pressure': 'pressure_msl',
            # Weather code
            'weather_code': 'weather_code', 'weathercode': 'weather_code'
        }
        
        # Rename columns
        for old_col, new_col in column_mapping.items():
            if old_col in df_weather.columns:
                df_weather[new_col] = df_weather[old_col]
        
        # Ensure all required columns exist
        required_cols = ['temperature', 'relative_humidity', 'precipitation', 'rain', 
                        'cloud_cover', 'wind_speed', 'wind_direction', 'wind_gusts', 
                        'pressure_msl', 'weather_code', 'location']
        
        for col in required_cols:
            if col not in df_weather.columns:
                df_weather[col] = 0  # Default value
        
        # Add is_day (you might need to calculate this from timestamp)
        if 'is_day' not in df_weather.columns:
            df_weather['is_day'] = True  # Default to daytime
        
        # Clean data
        numeric_cols = ['temperature', 'relative_humidity', 'precipitation', 'rain', 
                       'cloud_cover', 'wind_speed', 'wind_direction', 'wind_gusts', 
                       'pressure_msl', 'weather_code']
        
        for col in numeric_cols:
            df_weather[col] = pd.to_numeric(df_weather[col], errors='coerce').fillna(0)
        
        df_weather['weather_metric_key'] = range(1, len(df_weather) + 1)
        
        print(f"Transformed {len(df_weather)} weather records")
        return df_weather[['weather_metric_key', 'location', 'temperature', 'relative_humidity', 
                          'precipitation', 'rain', 'cloud_cover', 'wind_speed', 'wind_direction',
                          'wind_gusts', 'pressure_msl', 'weather_code', 'is_day']]
    
    def transform_complaint_data(self, df_complaints, dim_airline):
        """Transform complaint data using the exact column structure"""
        if df_complaints.empty:
            print("No complaint data to transform")
            return pd.DataFrame()
            
        print("Transforming complaint data...")
        print(f"Input complaint data shape: {df_complaints.shape}")
        print(f"Complaint data columns: {df_complaints.columns.tolist()}")
        
        # Make a copy to avoid modifying the original
        df = df_complaints.copy()
        
        # Show first few rows to confirm structure
        print("\nFirst 3 rows of complaint data:")
        print(df[['Airline / Airport Name', 'Complaints per million pax', 'Uphold rate for consumers', 'Average award']].head(3))
        
        # Map the exact column names from your Excel files
        column_mapping = {
            'Airline / Airport Name': 'airline_name',
            'Complaints per million pax': 'complaints_per_million',
            'Uphold rate for consumers': 'uphold_rate',
            'Average award': 'average_award',
            'Total cases opened': 'total_complaints',
            'Total awarded': 'total_award_amount',
            'source_year': 'date_year'
        }
        
        # Rename columns to match our schema
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df[new_col] = df[old_col]
        
        # Clean airline names for matching with our dimension
        if 'airline_name' in df.columns:
            df['airline_name'] = df['airline_name'].astype(str).str.strip().str.upper()
            
            # Standardize airline names to match your flight data
            airline_mapping = {
                'AIR INDIA': 'Air India',
                'INDIGO': 'IndiGo', 
                'SPICEJET': 'SpiceJet',
                'VISTARA': 'Vistara',
                'GO FIRST': 'Go First',
                'AIRASIA': 'AirAsia'
            }
            
            df['airline_name'] = df['airline_name'].map(airline_mapping).fillna(df['airline_name'])
        
        # Merge with airline dimension
        df = df.merge(
            dim_airline,
            left_on='airline_name',
            right_on='airline_name',
            how='inner'
        )
        print(f"✓ Merged with airline dimension, {len(df)} records after merge")
        
        # Create primary key
        df['complaint_metric_key'] = range(1, len(df) + 1)
        
        # Handle year - use source_year if available, otherwise default
        if 'date_year' not in df.columns:
            df['date_year'] = 2023  # Default year
        
        # Convert metrics to proper numeric types
        if 'complaints_per_million' in df.columns:
            df['complaints_per_million'] = pd.to_numeric(df['complaints_per_million'], errors='coerce').fillna(0)
        
        if 'uphold_rate' in df.columns:
            # Convert uphold rate from decimal to percentage (0.2727 → 27.27)
            df['uphold_rate'] = (pd.to_numeric(df['uphold_rate'], errors='coerce').fillna(0) * 100).round(2)
        
        if 'average_award' in df.columns:
            df['average_award_per_complaint'] = pd.to_numeric(df['average_award'], errors='coerce').fillna(0)
        else:
            df['average_award_per_complaint'] = 0
        
        # Select final columns for the fact table
        result_columns = [
            'complaint_metric_key', 'date_year', 'airline_key',
            'complaints_per_million', 'uphold_rate', 'average_award_per_complaint'
        ]
        
        # Ensure all required columns exist
        for col in result_columns:
            if col not in df.columns:
                if col == 'complaints_per_million':
                    df[col] = 0
                elif col == 'uphold_rate':
                    df[col] = 0
                elif col == 'average_award_per_complaint':
                    df[col] = 0
        
        final_result = df[result_columns]
        print(f"✓ Transformed {len(final_result)} complaint records")
        
        return final_result
    
    def load_to_warehouse(self, table_name, dataframe):
        """Load data into data warehouse with proper foreign key handling"""
        if dataframe.empty:
            print(f"No data to load for {table_name}")
            return
            
        cursor = self.dw_conn.cursor()
        try:
            # First, disable foreign key checks
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            # For all tables, use DELETE then reset auto-increment
            cursor.execute(f"DELETE FROM {table_name}")
            cursor.execute(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1")
            
            # Insert data
            for _, row in dataframe.iterrows():
                cols = ', '.join([f"`{col}`" for col in dataframe.columns])
                placeholders = ', '.join(['%s'] * len(row))
                sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
                cursor.execute(sql, tuple(row))
            
            # Re-enable foreign key checks
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            self.dw_conn.commit()
            print(f"✓ Loaded {len(dataframe)} rows into {table_name}")
            
        except Error as e:
            print(f"✗ Error loading {table_name}: {e}")
            self.dw_conn.rollback()
        finally:
            cursor.close()
    
    def run_etl(self):
        """Run the complete ETL process"""
        try:
            print("=" * 50)
            print("STARTING FLIGHT DATA WAREHOUSE ETL PROCESS")
            print("=" * 50)
            
            # Step 1: Create database connections
            self.create_connections()
            
            # Step 2: Extract data from all sources
            df_flights = self.extract_flight_data()
            df_weather = self.extract_weather_data()
            df_complaints = self.extract_complaint_data()
            df_forecast = self.extract_flight_forecast_data()  # Optional
            
            if df_flights.empty:
                print("CRITICAL: No flight data found. ETL cannot continue.")
                return
            
            # Step 3: Transform dimensions
            dim_airline, dim_route, dim_flight = self.transform_dimensions(df_flights)
            
            # Step 4: Transform facts
            fact_flight = self.transform_fact_flight_metrics(df_flights, dim_airline, dim_route, dim_flight)
            fact_weather = self.transform_weather_data(df_weather)
            fact_complaints = self.transform_complaint_data(df_complaints, dim_airline)
            
            # Step 5: Load to data warehouse
            print("\n" + "=" * 30)
            print("LOADING DATA TO WAREHOUSE")
            print("=" * 30)
            
            self.load_to_warehouse('dim_airline', dim_airline)
            self.load_to_warehouse('dim_route', dim_route)
            self.load_to_warehouse('dim_flight', dim_flight)
            self.load_to_warehouse('fact_flight_metrics', fact_flight)
            
            if not fact_weather.empty:
                self.load_to_warehouse('fact_weather_metrics', fact_weather)
            
            if not fact_complaints.empty:
                self.load_to_warehouse('fact_complaint_metrics', fact_complaints)
            
            print("\n" + "=" * 50)
            print("ETL PROCESS COMPLETED SUCCESSFULLY!")
            print("=" * 50)
            
        except Exception as e:
            print(f"\n✗ ETL process failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.close_connections()

# Run the ETL process
if __name__ == "__main__":
    etl = FlightDataETL()
    etl.run_etl()