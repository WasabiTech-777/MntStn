import logging
import os

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class helper:
    def downloadEdgarIndexFileAndGetPath(response, qtr, year):
        edgarIndexFileDownloadPath = f"{os.path.dirname(__file__)}\\resources\edgar-full-index-archives\master-{year}-QTR{qtr}.txt"
        LOGGER(f"Downloading the master Edgar Index File to: {edgarIndexFileDownloadPath}")

        # TODO: Update exception handling and above code with a real logger
        with open(edgarIndexFileDownloadPath, "wb") as f:
            f.write(response.content)
        if not f.closed:
            try:
                os.remove(edgarIndexFileDownloadPath)
            except OSError as e:  
                LOGGER.error("Error downloading and processing the Edgar Index file - rerun as it now most likely contains corrupted data: %s - %s." % (e.filename, e.strerror))

        return edgarIndexFileDownloadPath