import urllib2
import os
import threading

class DownloadThread (threading.Thread):
    def __init__(self, songID):
        threading.Thread.__init__(self)
        self.songID = songID
    def run(self):
		print self.songID
		songPath = "song-infos/%d.xml"%self.songID
		url = "http://star.zing.vn/includes/fnGetSongInfo.php?id=%d"%self.songID
		if not os.path.exists(songPath):
			f = open(songPath,"w")
			for line in urllib2.urlopen(url):
				f.write(line)
			f.close()

MAX_THREAD = 32;
curr = 0;
threads=[None] * MAX_THREAD
for songID in range(24557):
	threads[curr] =DownloadThread(songID)
	threads[curr].start()
	curr += 1
	if curr == MAX_THREAD:
		while curr>0:
			curr -= 1
			threads[curr].join()
