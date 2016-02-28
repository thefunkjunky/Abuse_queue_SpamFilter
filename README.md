# Abuse_queue_SpamFilter
 This is a designed to identify spam tickets in our spam/abuse queue 
 at the datacenter I work at.  The difficulty in using traditional
 spam filtering methods is that they will always select legitimate abuse tickets,
 because they always contain the full, original spam text in the body. 
 The task is further complicated by the fact that I am not given access to the support api, so I
 used Selenium to automate the actual browser (not ideal, but it works).

 This script only works (well, worked) on the particular abuse queue at my work, 
 I leave it here as a reference for my methods for future Selenium projects.
 It no longer functions at work, as management found out about it and promptly changed the api
 and ticketing web interface to break the script.  

 When it was working, it consistently selected NO false positives, and missed NO false negatives.
 It saved approximately 2 hours of work that was typically assigned to system admins, who are too
 valuable to be wasting time on such a simple and tedius task.
