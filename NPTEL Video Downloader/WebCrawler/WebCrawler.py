from bs4 import BeautifulSoup as bs
import requests as req
import progressbar as pbar
from tqdm import tqdm
import logging

class WebCrawler:
    """The Class contains neccessary functions to download the NPTEL Videos"""
    logger = None

    def __init__(self):
        logging.basicConfig(filename="logs.log", filemode='w')
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

    def getSoup(self, link):
        """Returns beautiful soup for provided link"""
        self.logger.info("---------->In getSoup() function of class WebCrawler.........")

        soup = None
        try:
            response = req.get(link)
            data = response.text
            soup = bs(data, "html.parser")
            return soup
        except req.exceptions.RequestException:
            self.logger.error("===================>Error in getting response for the given link: "+str(link))
        except:
            self.logger.error("===================>Error in getting soup for the given link: "+str(link))
        return None

    def getDownloadUrl(self, courseLink):
        """Returns download urls of all videos of the course link provided"""
        self.logger.info("In getDownloadUrl() function of class WebCrawler.........")
        try:
            soup = self.getSoup(courseLink)
            self.logger.info("=======>Getting soup for given course link is successfull")

            ul = soup.find_all('ul', {"class": "nav nav-tabs video-tabs"})

            requiredUrlLiTag = ""
            isRequiredUrlFound = False
            for each_ul in ul:
                if not isRequiredUrlFound:
                    li = each_ul.find_all('li')
                    for each_li in li:
                        if ('subjectid') in str(each_li):
                            requiredUrlLiTag = each_li
                            isRequiredUrlFound = True
                            break
            requiredUrlATag = requiredUrlLiTag.find('a')
            requiredUrlHref = requiredUrlATag.get("href")
            requiredUrlHref = str(requiredUrlHref)
            requiredUrl = requiredUrlHref.split('/')[1]
            downloadUrl = "https://nptel.ac.in/courses/" + requiredUrl

            self.logger.info("=======>Getting downloadURL for given course link is successfull")
            self.logger.info("=======>"+downloadUrl)

            return downloadUrl
        except:
            self.logger.error("=======>Error in getting downloadUrl for the course link")
            return None

    def downloadVideos(self, downloadUrl, pathToStoreTheFile):
        """This function downloads all the videos and save those to the path provided """
        requiredATag = []

        self.logger.info("In downloadVideos() function of class WebCrawler.........")

        soup = self.getSoup(downloadUrl)
        self.logger.info("=======>Getting soup for given downloadUrl link is successfull")

        try:
            rows = soup.find_all("a")
            for requiredRows in rows:
                if "mp4" in str(requiredRows):
                    requiredATag.append(requiredRows)

            self.logger.info("=======>Number of Files to Download: "+str(len(requiredATag)))
            print("Number of Files to Download: "+str(len(requiredATag)))
            pbar = tqdm(total=len(requiredATag))
        except:
            self.logger.error("=======>Error in retrieving download urls of video files")
            return None

        self.logger.info("=======>Started Downloading Videos...")

        for i in range(1,len(requiredATag)+1):
            fileName = None
            try:
                requiredDownloadUrl = requiredATag[i-1].get("href")
                fileName = requiredDownloadUrl.split("=")[-1]
                requiredDownloadUrl = "https://nptel.ac.in" + requiredDownloadUrl

                self.logger.info("=======>Downloading video number "+str(i)+" ["+fileName+"]")

                r = req.get(requiredDownloadUrl, stream=True)

                if pathToStoreTheFile[-1]!='/':
                    pathToStoreTheFile += '/'

                fileName = str(i)+" "+fileName
                with open(pathToStoreTheFile+fileName+".mp4", 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)

                pbar.update(1)
                self.logger.info("=======>Succesfully downloaded video number " + str(i) + " [" + fileName + "]")
            except:
                self.logger.error("=======>Error in Downloading video number " + str(i) + " [" + fileName + "]")
                return None

        self.logger.info("All videos downloaded successfully to the path: "+pathToStoreTheFile)


#Code Starts Here!!!
print("Welcome To Nptel Course Video Downloader!!!")
print("Enter Your Course Url:")
courseUrl = str(input().strip())
print("Enter Full Path To Store the Files:")
pathToStoreTheFile = str(input().strip())

webcrawler = WebCrawler()
downloadUrl = webcrawler.getDownloadUrl(courseUrl)

if not downloadUrl==None:
    webcrawler.downloadVideos(downloadUrl, pathToStoreTheFile)
    webcrawler.logger.info("Thank You!!!....")
else:
    webcrawler.logger.error("There was an in Retrieving the download url....")
    webcrawler.logger.error("Kindly try after some time....")
    webcrawler.logger.error("Thank You!!!....")

