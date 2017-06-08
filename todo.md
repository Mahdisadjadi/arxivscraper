## To-do list (code)

* Add command line option to run
* Add functions to filter out the results of API calls based on subcategories
or title/abstract containing specific terms.


## To-do list (documentation)
On command line
`python arxivscraper.py [-c|categories] [-f|from] [-u|until] [-w|waitingtime]`

* `-c`: No default value
* `-f`: Default first day of the current month
* `-u`: Default today
* `-w`: Default: 30 sec
`python arxivscraper.py -c physics -f 2017-06-01 -u 2017-06-06`

Note that the date is in `YYYY-MM-DD` format.

At each `API` call, only 1000 records are returned. The scripts waits 30 seconds to make the next call. You can change the waiting time (in seconds) between calls by `-w` flag. Example:

`python arxivscraper.py -c physics -f 2017-06-01 -u 2017-06-06 -w 20`

* The retrieved results also include records updated during the date range even if there created out of this range.
* to access help, `-h`
* To list all categories: to see a list of categories, see [here]().
