import airplane_price_tracker


# record_flights(popular_airports['Utah'])

origin = input("What state are you traveling from?(Please respond in initial caps) ")
date_from = input("What is the earliest date you plan on leaving?(yyyy-mm-dd) ")
date_to = input("What is the latest date you plan on leaving?(yyyy-mm-dd) ")
return_from = input("What is the earliest date you plan on returning?(yyyy-mm-dd) ")
return_to = input("What is the latest date you plan on returning?(yyyy-mm-dd) ")
c = airplane_price_tracker.DrivingFlying(origin, date_from, date_to, return_from, return_to)
c.record_flights()



