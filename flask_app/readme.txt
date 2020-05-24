If you want to know what does specific function do read the comment above it.

First open flask_app.py in python. When you go to the website you are presented with 4 options.
DaniaLabs is the name I chose for this project and would take you to some sort of about page with different information regarding this site.
Home is simply a starting page. Sign Up takes you to a place where you can sign up while mmeting some requirements (password lenght ect.).
If you have signed up you can move to the login page on which you need to provide your information. 
Your data is stored in database and password is encrypted. When you sign up you are assigned no role by default.
If you want to have admin role you need to change that in database or use already existing account.
The accounts are:
USERNAME: test PASSWORD: Testtest ROLE: none
USERNAME: user PASSWORD: Useruser ROLE: none
USERNAME: admin PASSWORD: Adminadmin ROLE: admin
Once you are signed up you can visit labs, bookings, calendar and dashboard. You can also log out by clicking button.
Settings and profile are empty for now.
If you log in as admin you can also acces physical resources and virtual resources.
In both of them admin can manage all data.
If you visit Labs you are presented with all labs. Admin can manage them.
If you visit Bookings you can view, add and delete your bookings. Admin can see and manage ALL users bookings.
If you visit Calendar you are presented with calendar.
On all of those sites there is a button to go back to dashboard.
If you type some kind of data wrong while inserting it into database you will be presented with site telling you that you did that.
From that site you can go back by clicking button.
If you mistype any site "/" you will be presented with page saying that the page you look for doesn't exist.

