import pandas as pd
import sqlalchemy as db
import pandas as pd
import sqlalchemy as db
import math

from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show


class DataProcessor:
    def __init__(self, training_files, ideal_file, test_file):
        self.training_files = training_files
        self.ideal_file = ideal_file
        self.test_file = test_file
        self.engine = db.create_engine('sqlite:///data.db')
        self.connection = self.engine.connect()

    def load_data(self):
        db_loader = DatabaseLoader(self.engine)
        db_loader.load_training_data(self.training_files)
        db_loader.load_ideal_functions(self.ideal_file)
        db_loader.load_test_data(self.test_file)

    def choose_ideal_functions(self):
        ideal_selector = IdealFunctionSelector(self.engine)
        self.ideal_functions = ideal_selector.select_ideal_functions()

    def map_test_data(self):
        test_mapper = TestDataMapper(self.engine)
        test_mapper.map_data(self.ideal_functions)

    def visualize_data(self):
        visualizer = DataVisualizer(self.engine)
        visualizer.visualize()

class DatabaseLoader:
    def __init__(self, engine):
        self.engine = engine

    def load_training_data(self, training_files):
        for i, file in enumerate(training_files):
            try:
                df = pd.read_csv(file)
                df.to_sql(f'training_{i+1}', self.engine, index=False, if_exists='replace')
            except Exception as e:
                print(f"Error loading training data from {file}: {e}")

    def load_ideal_functions(self, ideal_file):
        df = pd.read_csv(ideal_file)
        df.to_sql('ideal_functions', self.engine, index=False, if_exists='replace')

    def load_test_data(self, test_file):
        df = pd.read_csv(test_file)
        df.to_sql('test_data', self.engine, index=False, if_exists='replace')

class IdealFunctionSelector:
    def __init__(self, engine):
        self.engine = engine
        self.connection = self.engine.connect()

    def calculate_deviation(self, ideal_function):
        try:
            query = db(
                f"SELECT SUM(POWER((t.y{ideal_function} - i.y{ideal_function}), 2)) AS deviation FROM training_{ideal_function} t JOIN ideal_functions i ON t.x = i.x")
            result = self.connection.execute(query)
            deviation = result.fetchone()[0]
            return deviation if deviation is not None else 0
        except Exception as e:
            print(f"Error executing SQL query: {e}")

    def select_ideal_functions(self):
        deviations = {}
        for i in range(50):
            deviation = self.calculate_deviation(i + 1)
            if deviation is not None:
                deviations[i + 1] = deviation
        if deviations:  # Check if deviations dictionary is not empty
            sorted_deviations = sorted(deviations.items(), key=lambda x: x[1])
            ideal_functions = [x[0] for x in sorted_deviations[:4]]
            print("Selected ideal functions:", ideal_functions)
            return ideal_functions
        else:
            print("No valid ideal functions found.")
            return []

class TestDataMapper:
    def __init__(self, engine):
        self.engine = engine
        self.connection = self.engine.connect()

    def map_data(self, ideal_functions):
        for ideal_func in ideal_functions:
            query = f"SELECT * FROM test_data WHERE ABS(y - (SELECT y{ideal_func} FROM ideal_functions WHERE x = test_data.x)) <= (SELECT MAX(ABS(y - y{ideal_func})) * SQRT(2) FROM training_{ideal_func})"
            result = self.connection.execute(query)
            mapped_data = result.fetchall()
            print(f"Test data mapped to ideal function {ideal_func}: {mapped_data}")

class DataVisualizer:
    def __init__(self, engine):
        self.engine = engine
        self.connection = self.engine.connect()

    def visualize(self):
        p = figure(title="Data Visualization", x_axis_label='X', y_axis_label='Y')

        # Plot training data
        for i in range(1, 1):
            query = f"SELECT X, Y{i} FROM training_{i}"
            df = pd.read_sql_query(query, self.engine)
            p.circle(df['x'], df[f'y{i}'], color="blue", legend_label=f'Training {i}', size=5)

        # Plot ideal functions
        for i in range(1, 1):
            query = f"SELECT x, y{i} FROM ideal_functions"
            df = pd.read_sql_query(query, self.engine)
            p.line(df['x'], df[f'y{i}'], color="green", legend_label=f'Ideal {i}', line_width=2)

        # Plot mapped test data with deviations
        for i in range(1, 1):
            query = f"SELECT x, y, {i}_deviation FROM test_data WHERE {i}_deviation IS NOT NULL"
            df = pd.read_sql_query(query, self.engine)
            source = ColumnDataSource(df)
            p.circle('x', 'y', source=source, color="red", legend_label=f'Mapped Test Data {i}', size=8)

        p.legend.location = "top_left"
        show(p)

class UnitTester:
    def __init__(self, data_processor):
        self.data_processor = data_processor

    def run_tests(self):
        # Placeholder for unit tests
        print("Unit tests will be implemented here")

def main():
    training_files = ['train.csv']
    ideal_file = 'ideal.csv'
    test_file = 'test.csv'

    data_processor = DataProcessor(training_files, ideal_file, test_file)
    data_processor.load_data()
    data_processor.choose_ideal_functions()
    data_processor.map_test_data()
    data_processor.visualize_data()

    # unit_tester = UnitTester(data_processor)
    # unit_tester.run_tests()

if __name__ == "__main__":
    main()
