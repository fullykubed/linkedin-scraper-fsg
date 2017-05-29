from tkinter import filedialog, messagebox, Tk, Entry, Button, Label, W

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import csv


class LinkedInScraper:


    def __init__(self):

        self.driver = webdriver.Chrome()


        self.scrape()

        self.driver.close()

    ###################################
    ##  Driver
    ###################################

    def scrape(self, numRetry=1):

        #pull data from csv
        inputFile = self.getInputFile()
        inputData = self.loadSearchData(inputFile)

        #login
        self.getCredentials()
        self.driver.get('http://www.linkedin.com')

        outputData = []
        failed = []

        for i in range(len(inputData)):

            #get the url
            if inputData[i][3] == '':
                url = self.search(inputData[i][0] + " " + inputData[i][1] + " " + inputData[i][2])
                inputData[i][3] = url
            else:
                url = inputData[i][3]


            if url == '':
                outputData.append(['Not found'])
                failed.append(i)
                continue

            self.driver.get(url)
            outputData.append(self.extractExperiences(True))


        #circle back for the failed lookups
        while(numRetry > 0):

            for j in range(len(failed)):
                i = failed[j]

                url = self.search(inputData[i][0] + " " + inputData[i][1] + " " + inputData[i][2])

                if url == '':
                    continue

                outputData[i].pop()
                self.driver.get(url)
                outputData.append(self.extractExperiences(True))

            numRetry -= 1


        #write the data
        self.writeSearchData(inputFile[:-4]+ "_out.csv", inputData, outputData)



    ###################################
    ##  Business Logic
    ###################################

    def getCredentials(self):
        master = Tk()
        master.title("LinkedIn Credentials")

        w = 350  # width for the Tk root
        h = 100  # height for the Tk root

        # get screen width and height
        ws = master.winfo_screenwidth()  # width of the screen
        hs = master.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)

        # set the dimensions of the screen
        # and where it is placed
        master.geometry('%dx%d+%d+%d' % (w, h, x, y))


        Label(master, text="Username").grid(row=0)
        Label(master, text="Password").grid(row=1)

        e1 = Entry(master)
        e2 = Entry(master, show="*")

        e1.grid(row=0, column=1)
        e2.grid(row=1, column=1)

        def callback():
            username = e1.get()
            password = e2.get()
            master.destroy()
            self.login(username,password)


        Button(master, text='Execute Script', command=callback).grid(row=3, column=0, sticky=W, pady=4)
        master.mainloop()


    def login(self, username, password):
        elem = self.driver.find_element_by_name('session_key')
        elem.send_keys(username)

        elem = self.driver.find_element_by_name('session_password')
        elem.send_keys(password)

        elem.send_keys(Keys.RETURN)


    def search(self, key):
        elem = self.driver.find_element_by_xpath("//input[@placeholder='Search']")
        elem.send_keys(key)
        elem.send_keys(Keys.RETURN)

        try:
            elem = WebDriverWait(self.driver, 2, poll_frequency=0.1).until(
                EC.presence_of_element_located((By.CLASS_NAME, "results-list"))
            )
            elems = elem.find_elements_by_tag_name('a')

            return elems[0].get_attribute('href')

        except TimeoutException:
            return ''


    def extractExperiences(self, currentOnly=False):

        elem = WebDriverWait(self.driver, 2, poll_frequency=0.1).until(
                EC.presence_of_element_located((By.CLASS_NAME, "experience-section"))
            )
        elems = elem.find_elements_by_class_name('pv-profile-section__card-item')

        experiences = []


        for elem in elems:
            meta = elem.find_element_by_class_name('pv-entity__summary-info')


            if (not currentOnly or 'Present' in meta.find_element_by_class_name('pv-entity__date-range').text):
                jobInfo = [meta.find_element_by_tag_name('h3').text,
                           meta.find_element_by_class_name('pv-entity__secondary-title').text,
                           meta.find_element_by_class_name('pv-entity__location').text[9:]]



                experiences.extend(jobInfo)

        return experiences


    ###################################
    ##  Input Loading
    ###################################


    def getInputFile(self):
        root = Tk()
        root.overrideredirect(1)
        root.withdraw()

        messagebox.showinfo("Select Search Information",
                            "In the next prompt, select your SEARCH INFORMATION.")
        while (True):
            inputFile= filedialog.askopenfilename()
            if inputFile:
                break
            messagebox.showerror("Error: Select File",
                                 "You must select the search information!")


        root.destroy()
        return inputFile


    def loadSearchData(self, input):
        with open(input) as f:
            reader = csv.reader(f)
            searchData = []
            next(reader)
            for row in reader:
                searchData.append(row)

        return searchData


    ###################################
    ##  Writing
    ###################################

    def writeSearchData(self, output, inputData, outputData):
        with open(output, "w+") as f:
            writer = csv.writer(f)
            writer.writerow(['First Name', 'Last Name', 'Auxiliary (Input)', 'URL', 'Search Info'])
            for i,row in enumerate(inputData):
                row.extend(outputData[i])
                writer.writerow(row)


def main():
    LinkedInScraper()

if __name__ == "__main__":
    LinkedInScraper()