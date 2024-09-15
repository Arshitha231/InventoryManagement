import mysql.connector as m
con=m.connect(host='localhost',user='root',password='root',charset='utf8',database='inventory')
cur=con.cursor()

def show_main():
      print("1. Add product")
      print("2. Show product")
      print("3. Update stock")
      print("4. exit")


repeat =  True
while(repeat):
   show_main()
   choice = int(input("Select an option"))
   if choice==1:
      prod_id = int(input("Enter prod_id"))
      product_name = input("Enter product name")
      category = input ("Enter product type or category")
      qty = int(input ("Enter qty in stock"))
      price = float(input("Enter price"))
      supplier_id= int(input("Enter supplier id"))
      q = """insert ignore into PRODUCT values(%s, %s, %s, %s , %s, %s)"""
      cur.execute(q, (prod_id, product_name, category, qty, price, supplier_id))
   elif choice==2:
      cur.execute("select * from product")
      data=cur.fetchall()
      for x in data:
         print(x)
   elif choice==3:
      print()
   else:
      print("Thank you for using Inventory Mangement")
      repeat = False
      
      
#cur.execute("insert ignore into PRODUCT values(401,'bearings','electrical',15,160.00,201)")
con.commit()
cur.close()
con.close()

            
