
import psycopg2


# connection to the existing database (use your own credentials)
def db_connect():
    return psycopg2.connect(user='postgres', \
                            password='realmandwes123', \
                            host='localhost', \
                            port='5432', \
                            database='Pet Store')


# close the db connection
def db_close(connection):
    connection.close()


# function to make insert queries
def make_insert_query(cursor, query, connection):
    cursor.execute(query)
    connection.commit()


# function to make select queries
def make_select_query(cursor, query):
    cursor.execute(query)
    return cursor


# display menu options for users
def menu_options(is_authenticated, current_user, cursor):
    if not is_authenticated:
        print(f"Welcome {current_user}")
        print("1. Register", "2. Login", "3. Exit", sep='\n')
    else:
        user_name = make_select_query(cursor, f"select user_name from users where user_login = '{current_user}'").fetchone()[0]
        print(f"Welcome {user_name}")
        print("1. Buy pets", "2. Buy products", "3. My purchases", "4. Exit", sep='\n')


# make user registration
def user_registration(cursor, connection):
    form = ['Login', 'First Name', 'Last Name', 'Password', 'Repeat password', 'Address', 'Phone number']  # list of forms
    user_form = dict.fromkeys(form)  # create dictionary from form items
    unique_login = False  # checking username for uniqueness
    for i in form:  # running through each option in the form and fill it
        if i == 'Login':  # checking the login
            while not unique_login:  # loop until user enter a unique login
                user_form[i] = input("Enter your " + i + ": \n")
                for j in make_select_query(cursor, "select user_name from users").fetchall():
                    if user_form.get('Login') in j:
                        print("This username is already exists, please choose another!")
                        break
                else:  # if everything is ok then we proceed to the next items of form
                    unique_login = True

        else:
            user_form[i] = input("Enter your " + i + ": \n")
    # taking total number of users to create a user id for a new user
    user_id = int(make_select_query(cursor, "select count(*) from users").fetchall()[0][0]) + 1
    # creating the query itself
    query = f"insert into users values(\
                    {user_id},\
                    '{user_form['Login']}',\
                    '{user_form['First Name']}',\
                    '{user_form['Last Name']}', \
                    '{user_form['Password']}',\
                    '{user_form['Address']}', \
                    '{user_form['Phone number']}' \
                    )"
    # calling function for insertion
    make_insert_query(cursor, query, connection)


# function to get signed into the system
def login(cursor, connection):
    user_login = input("Input your login: ")
    password = input("Your password: ")
    global current_user
    global is_authenticated
    if password == make_select_query(cursor, f"select user_password from users where user_login='{user_login}'").fetchone()[0]:
        is_authenticated = True
        current_user = user_login
        user_id = make_select_query(cursor, f"select user_id from users where user_login = '{current_user}'").fetchone()[0]
        make_insert_query(cursor, f"insert into sold_products values ({user_id}, 0, 0, 0, 0, 0)", connection)
    else:
        print("Your login or password is wrong!")
        login(cursor)


# global variables to use in different functions
is_authenticated = False
current_user = "Guest"

#function for buying pets
def buy_pets(cursor, connection):
    print("Choose pet:\n" )
    cursor.execute("SELECT * from pets")
    for i in cursor.fetchall():
        print("Id = ", i[0], )
        print("Pet category = ", i[1])
        print("Breed = ", i[2])
        print("Price  = ", i[3])
        print("Quantity  = ", i[4], "\n")
    chosen_pet = input("Choose pet's ID: ")
    quantity = int(input("Choose quantity: "))
    user_id = make_select_query(cursor, f"select user_id from users where user_login = '{current_user}'").fetchone()[0]
    pet_name = make_select_query(cursor, f"select pet_category from pets where pet_id = {chosen_pet}").fetchone()[0]
    cost = make_select_query(cursor, f"select cost from pets where pet_id = {chosen_pet}").fetchone()[0]
    if chosen_pet == str(make_select_query(cursor, f"select pet_id from pets where pet_id={chosen_pet}").fetchone()[0]):
        query_for_pets = f"UPDATE sold_products SET user_id = {user_id}, pet_name = '{pet_name}' WHERE user_id = '{user_id}'"
        query_for_pets_update = f"UPDATE pets SET quantity = quantity-{quantity} WHERE pet_id = '{chosen_pet}'"
        make_insert_query(cursor, query_for_pets, connection)
        make_insert_query(cursor, f"UPDATE sold_products SET pet_quantity = pet_quantity+{quantity}, total = total+({cost}*{quantity}) WHERE user_id = '{user_id}'", connection)
        make_insert_query(cursor, query_for_pets_update, connection)

def buy_products(cursor, connection):
    print("Choose product:\n" )
    cursor.execute("SELECT * from pet_products")
    for i in cursor.fetchall():
        print("Id = ", i[0], )
        print("Product = ", i[1])
        print("Type = ", i[2])
        print("For  = ", i[4])
        print("Cost = ", i[3])
        print("Quantity  = ", i[5], "\n")
    chosen_product = input("Choose product's ID: ")
    quantity = int(input("Choose quantity: "))
    user_id = make_select_query(cursor, f"select user_id from users where user_login = '{current_user}'").fetchone()[0]
    pp_name = make_select_query(cursor, f"select pp_name from pet_products where pp_id = {chosen_product}").fetchone()[0]
    cost = make_select_query(cursor, f"select cost from pet_products where pp_id = {chosen_product}").fetchone()[0]
    if chosen_product == str(make_select_query(cursor, f"select pp_id from pet_products where pp_id={chosen_product}").fetchone()[0]):
        query_for_products = f"UPDATE sold_products SET user_id = {user_id}, pp_name = '{pp_name}' WHERE user_id = '{user_id}'"
        query_for_products_update = f"UPDATE pet_products SET quantity = quantity-{quantity} WHERE pp_id = '{chosen_product}'"
        make_insert_query(cursor, query_for_products, connection)
        make_insert_query(cursor, f"UPDATE sold_products SET pp_quantity = pp_quantity+{quantity}, total = total+({cost}*{quantity}) WHERE user_id = '{user_id}'", connection)
        make_insert_query(cursor, query_for_products_update, connection) 
        
def sold_products(cursor):
    user_id = make_select_query(cursor, f"select user_id from users where user_login = '{current_user}'").fetchone()[0]
    #cursor.execute("SELECT (sum(pp_quantity), sum(pet_quantity), sum(total)) from sold_products WHERE user_id = '{user_id}'")
    #for i in cursor.fetchall():
    print("Name = ", make_select_query(cursor, f"select user_name from users where user_login = '{current_user}'").fetchone()[0])
    print("Product quantity = ", make_select_query(cursor, f"select sum(pp_quantity) from sold_products WHERE user_id = '{user_id}'").fetchone()[0])
    print("Pet quantity = ", make_select_query(cursor, f"select sum(pet_quantity) from sold_products WHERE user_id = '{user_id}'").fetchone()[0])
    print("Total sum  = ", make_select_query(cursor, f"select sum(total) from sold_products WHERE user_id = '{user_id}'").fetchone()[0], "\n")
        
# the main algorithm of the program
def main():
    connection = db_connect()
    cursor = connection.cursor()
    while is_authenticated == False:
        menu_options(is_authenticated, current_user, cursor)
        choose_option = input("Please choose what to do: ")
        if choose_option == '1':
            user_registration(cursor, connection)
        elif choose_option == '2':
            login(cursor, connection)
        elif choose_option == '3':
            break
        else:
            print("Please choose 1 or 2")
            continue
            
    while is_authenticated == True:
        menu_options(is_authenticated, current_user, cursor)
        choose_option = input("Please choose what you want to buy: ")
        print("\n")
        if choose_option == '1':
            buy_pets(cursor, connection)
        elif choose_option == '2':
            buy_products(cursor, connection)
        elif choose_option == '3':
            sold_products(cursor)
        elif choose_option == '4':
            break
        else:
            print("Please choose 1 or 2")
            continue


# calling the main function
if __name__ == '__main__':
    main()