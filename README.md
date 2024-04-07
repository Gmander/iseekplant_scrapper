# To run initially
1. Pull repo
2. Navigate there in terminal
3. Have Docker
4. Run `docker build -t <image_name> .` to build image
	5. Ex. `docker build -t isp-scrape .`
5. Run the script with your path to pwd and desired args
	1. `run -v <your_pwd_here>:/app <image_name> python isp_scrapper.py <arg_1> <arg_2> <arg_3> <arg_4> <arg_5> `
	2. EX. <br> `docker run -v C:\Users\AidanPC\projects\ispS:/app isp-scrape python isp_scrapper.py 'excavator-hire' 1 3 5 True`
    3. Argument breakdown:
		1. arg_1: Desired subcategory and thus URL injection. <br> - Format must match url standards: 'Excavator Hire' -> 'excavator-hire' <br> - Known acceptable inputs below. <br> 
![image](https://github.com/Gmander/iseekplant_scrapper/assets/68246180/a3fb04a2-9ad1-4009-ab20-3e29ce66cda4)
		3. arg_2: start_page as int (Typically 1 if not wanting to start somewhere else)
		4. arg_3: end_page as int (or 0 if you want to run all available pages)
		5. arg_4: min_accepted_blanks as int. This is the minimum number of companies you will allow to have N/A for an address. Some company pages have to be visited twice to collect it, some are actually blank. Leave as 0 if doing a small number of pages, past that 5 is a safe number. It will run continuously and eventually fail if there are more companies with no address than you allow for.
		6. arg_5: clear_csv as Bool. This value dictates if the scrapper clears existing data, or continues to integrate newly scrapped data into your existing csv.
	4. This command runs the script in a docker container, but sets your computer's path as the desired output for the csv

# To update after initial run
- If you have already run the scrapper and would like to update any addresses that are showing up as 'N/A', perform the following steps
   - Running this will look through all companies in your current csv/json and research all that have a 'N/A' in the address field
   - Some addresses show up as 'N/A' when scrapping more than 5 pages at a time.
1. Build the image if you have not already following instructions above
2. Navigate to directory with script in terminal
3. Run the script with your path to pwd and 'recursive_update' as <arg_1> and your desired min_accepted_blanks (as discussed above) as <arg_2>
  1. `docker run -v <your_pwd_here>:/app <image_name> python isp_scrapper.py 'recursive_update' <arg_2>`
  2. Ex. `docker run -v C:\Users\AidanPC\projects\ispS:/app isp-scrape python isp_scrapper.py 'recursive_update' 5`
