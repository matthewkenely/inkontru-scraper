class Inkontru_Event():
    def __init__(self):
        self.event_name = ""
        self.dates = []
        self.location = ""
        self.time = ""
        self.duration = ""
        self.audience_level = ""
        self.fee = ""
        self.entity = ""
        self.link = ""

    def show(self):
        print("event_name:", self.event_name)
        print("dates:", self.dates)
        print("location:", self.location)
        print("time:", self.time)
        print("duration:", self.duration)
        print("audience_level:", self.audience_level)
        print("fee:", self.fee)
        print("entity:", self.entity)
        print("link:", self.link)

    def as_list(self):
        return [self.link, self.event_name, self.dates, self.location, self.time, self.duration, self.audience_level, self.fee, self.entity]
    
    def as_dict(self):
        
        return {
            "link": self.link, 
            "name" : self.event_name, 
            "dates": self.dates, 
            "location": self.location, 
            "start_time": self.time, 
            "duration": self.duration, 
            "audience_level": self.audience_level, 
            "fee" : self.fee, 
            "entity": self.entity
        }