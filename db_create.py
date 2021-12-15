import sqlite3


def create_tables(database):
    """ Create database tables
    :param database: Database connection object
    :return:
    """
    # create SQL codes for table creation
    sql_create_configuration_table = """CREATE TABLE IF NOT EXISTS configuration (
                                             id integer PRIMARY KEY,
                                             name text NOT NULL UNIQUE,
                                             show_unknown_sensors integer NOT NULL,
                                             show_model integer NOT NULL,
                                             model_chamber_text text NOT NULL,
                                             model_control_text text NOT NULL
                                         );"""

    sql_create_sensor_table = """CREATE TABLE IF NOT EXISTS sensor (
                                      id integer PRIMARY KEY,
                                      configuration_id integer NOT NULL,
                                      short_name text NOT NULL,
                                      name text NOT NULL,
                                      physical_value text NOT NULL,
                                      physical_unit text NOT NULL,
                                      FOREIGN KEY (configuration_id) REFERENCES configuration (id) ON DELETE CASCADE
                                  );"""

    sql_create_tab_table = """CREATE TABLE IF NOT EXISTS tab (
                                  id integer PRIMARY KEY,
                                  configuration_id integer NOT NULL,
                                  name text NOT NULL,
                                  grid_width integer NOT NULL DEFAULT 5,
                                  grid_height integer NOT NULL DEFAULT 2,
                                  FOREIGN KEY (configuration_id) REFERENCES configuration (id) 
                                                                 ON DELETE CASCADE
                              );"""

    sql_create_cell_table = """CREATE TABLE IF NOT EXISTS cell (
                                   id integer PRIMARY KEY,
                                   tab_id integer NOT NULL,
                                   row integer NOT NULL,
                                   column integer NOT NULL,
                                   rowspan integer NOT NULL DEFAULT 1,
                                   colspan integer NOT NULL DEFAULT 1,
                                   FOREIGN KEY (tab_id) REFERENCES tab (id) ON DELETE CASCADE
                               );"""

    sql_create_sensor_cell_table = """CREATE TABLE IF NOT EXISTS sensor_cell (
                                          id integer PRIMARY KEY,
                                          sensor_id integer NOT NULL,
                                          cell_id integer NOT NULL,
                                          FOREIGN KEY (sensor_id) REFERENCES sensor (id) ON DELETE CASCADE,
                                          FOREIGN KEY (cell_id) REFERENCES cell (id) ON DELETE CASCADE
                                      );"""

    sql_create_address_table = """CREATE TABLE IF NOT EXISTS address (
                                      id integer PRIMARY KEY,
                                      ip_port text NOT NULL UNIQUE,
                                      use_datetime real NOT NULL
                                  );"""

    # execute SQL codes for table creation
    try:
        cursor = database.cursor()
        cursor.execute(sql_create_configuration_table)
        cursor.execute(sql_create_sensor_table)
        cursor.execute(sql_create_tab_table)
        cursor.execute(sql_create_cell_table)
        cursor.execute(sql_create_sensor_cell_table)
        cursor.execute(sql_create_address_table)
    except sqlite3.Error:
        raise


def main():
    """ Create the configuration database, its tables and add the default configuration """
    # create a new database
    database = None
    try:
        database = sqlite3.connect("configurations.db")
    except sqlite3.Error as error:
        print(error)
        return  # stop in case of an error

    # create tables if they don't exist
    try:
        create_tables(database)
    except sqlite3.Error as error:
        print(error)
        database.close()  # in case of an error close the connection to the DB
        return  # and stop

    database.close()


if __name__ == "__main__":
    main()