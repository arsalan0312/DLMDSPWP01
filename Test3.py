import pandas as pd
from sqlalchemy import create_engine
from bokeh.plotting import figure, output_file, show
import numpy as np


class DataLoader:
    def __init__(self):
        pass

    def load_training_data(self):
        training_data = pd.read_csv('train.csv')
        return training_data

    def load_ideal_functions(self):
        ideal_functions = pd.read_csv('ideal.csv')
        return ideal_functions

    def load_test_data(self):
        test_data = pd.read_csv('test.csv')
        return test_data


class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.engine = create_engine(f'sqlite:///{self.db_name}')

    def insert_data(self, data, table_name):
        try:
            data.to_sql(table_name, self.engine, if_exists='replace', index=False)
        except Exception as e:
            print(f"Error inserting data into {table_name}: {e}")

    def visualize_data(self, training_data, ideal_functions, mapped_test_data):
        plot_width = 1000  # Set your desired width
        plot_height = 600  # Set your desired height
        output_file("visualization.html")
        p = figure(title="Data Visualization", x_axis_label='X', y_axis_label='Y')
        p.width = plot_width
        p.height = plot_height
        # Plot training data
        for idx in training_data:
            p.circle(training_data['x'], training_data['y1'], legend_label='Training Data Y1', color='blue')

        # Plot ideal functions
        for idx in range(1, 51):  # Assuming y1 to y50 columns in ideal_functions
            p.line(ideal_functions['x'], ideal_functions[f'y{idx}'], legend_label=f'Ideal Function {idx}', line_color='red')
        #
        # # Plot mapped test data
        p.square(mapped_test_data['x'], mapped_test_data['y'], legend_label='Mapped Test Data', color='green')

        show(p)


class DataProcessor:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def process_training_data(self, training_data):
        self.db_manager.insert_data(training_data, 'training_data')

    def process_ideal_functions(self, ideal_functions):
        self.db_manager.insert_data(ideal_functions, 'ideal_functions')

    def process_test_data(self, test_data):
        self.db_manager.insert_data(test_data, 'test_data')

    def match_test_data_to_ideal_functions(self, test_data, ideal_functions):
        # Initialize variables to store the mapped test data and deviations
        mapped_test_data_list = []

        # Loop through each test data point
        for idx, test_point in test_data.iterrows():
            min_deviation = float('inf')
            mapped_function_index = None
            # min_deviation = 0

            # Calculate deviation for each ideal function
            for func_idx in range(1, 51):  # Assuming y1 to y50 columns in ideal_functions
                deviation = np.sqrt(np.sum((ideal_functions[f'y{func_idx}'] - test_point['y']) ** 2))
                if deviation < min_deviation:
                    min_deviation = deviation
                    mapped_function_index = func_idx

            # Map the test data point to the ideal function with the least deviation
            mapped_test_data_list.append({
                'x': test_point['x'],
                'y': test_point['y'],
                'mapped_ideal_function': mapped_function_index,
                'deviation': min_deviation
            })

        return pd.DataFrame(mapped_test_data_list)

    def save_results(self, mapped_test_data):
        # Save mapped test data and deviations into database
        self.db_manager.insert_data(mapped_test_data, 'mapped_test_data')


if __name__ == "__main__":
    data_loader = DataLoader()
    training_data = data_loader.load_training_data()
    ideal_functions = data_loader.load_ideal_functions()
    test_data = data_loader.load_test_data()

    db_manager = DatabaseManager('database.db')

    data_processor = DataProcessor(db_manager)
    data_processor.process_training_data(training_data)
    data_processor.process_ideal_functions(ideal_functions)
    data_processor.process_test_data(test_data)

    mapped_test_data = data_processor.match_test_data_to_ideal_functions(test_data, ideal_functions)
    data_processor.save_results(mapped_test_data)

    db_manager.visualize_data(training_data, ideal_functions, mapped_test_data)
