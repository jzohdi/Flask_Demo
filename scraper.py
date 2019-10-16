class ScheduleScraper:
    def __init__(self, BeautifulSoup, get, re):
        self.BS = BeautifulSoup
        self.get = get
        self.re = re
        self.__urls = {"CORE": "https://app.testudo.umd.edu/soc/202001/",
                       "GEN": "https://app.testudo.umd.edu/soc/gen-ed/202001/"}
        self.__our_umd_url = "http://www.ourumd.com/class/"

    def get_course_types(self):
        return self.__urls.keys()

    def __make_request(self, type, major):
        response = self.get(self.__urls[type] + major)
        if response.status_code == 200:
            return response.content
        else:
            return False

    def get_page(self, response):
        soup = self.BS(response, "html.parser")
        return soup

    def get_courses_by_major(self, type, major):

        course_list = []

        if type not in self.__urls:
            print(f"course type: {type} invalid")
            return course_list

        request = self.__make_request(type, major)

        if not request:
            print("Something went wrong.")
            return course_list
        soup = self.get_page(request)

        if type == "CORE":
            courses = soup.find("div", "courses-container").find_all("div", "course")
            for course in courses:
                course_credits = course.find("span", "course-min-credits").string
                course_id = course.find("div", "course-id").string
                course_name = course.find("span", "course-title").string

                course_obj = dict(Id=course_id, Name=course_name, Credits=course_credits)

                course_details = course.find("div", "approved-course-text")
                if course_details:
                    course_details = course_details.find("div").find("div").find_all("div")
                    for details in course_details:
                        title = details.find("strong").text
                        course_obj[title] = details.text.replace(title, "")

                course_list.append(course_obj)

        if type == "GEN":
            departments = soup.find_all("div", "course-prefix-container")

            for department in departments:
                courses = department.find_all("div", "courses-container")

                for course in courses:
                    course_id = course.find("div", "course-id").string
                    name = course.find("span", "course-title").string
                    course_credits = course.find("span", "course-min-credits").string
                    counts_for = []
                    gen_eds = course.find("div", "gen-ed-codes-group").find_all("a")

                    for gen_ed in gen_eds:
                        counts_for.append(gen_ed.string)

                    course_obj = dict(Id=course_id, Name=name, Credits=course_credits, GenEds=counts_for)
                    course_list.append(course_obj)

        return course_list

    def get_grades(self, course_id):

        response = self.get(self.__our_umd_url + course_id)

        if response.status_code != 200:
            return {"Average": "0", "Distribution": ["No grade data available"]}

        soup = self.BS(response.content, "html.parser")

        overall = soup.find("tr", "grade")
        if overall == None:
            return {"Average": "0", "Distribution": ["No grade data available"]}

        average = overall.find("td").string
        if average is None or average == "None":
            return {"Average": "0", "Distribution": ["No grade data available"]}

        distr = []
        break_down = overall.find_all("td", "first")

        for dist in break_down:
            distr.append(dist.string)

        return {"Average": average, "Distribution": distr}

    def add_grades_to_classes(self, class_list):
        for index in range(len(class_list)):
            course = class_list[index]
            course_id = course.get("Id")
            grades = self.get_grades(course_id)
            class_list[index]["Grades"] = grades

    @staticmethod
    def like(text, re):
        match_all = r'.*'
        string_ = text
        if not isinstance(string_, str):
            string_ = str(string_)
        regex = match_all + re.escape(string_) + match_all
        return re.compile(regex, flags=re.DOTALL)

    @staticmethod
    def sort_class_list(class_list):
        return sorted(class_list, key=lambda x: x.get("Grades").get("Average"), reverse=True)