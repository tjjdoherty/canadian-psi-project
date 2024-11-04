# canadian-psi-project
Analysis of Canadian Post-Secondary Institutions by unsupervised learning, growth and revenue modelling
An exploration of student demographics, program diversity, growth rates and provincial regulations.

## Goals of this project:

- Beginning with the province of Ontario, I will collect and combine key data on Canada's Post-Secondary Institution's student enrolment across major demographics e.g. Status in Canada, Gender, information on Program enrolment by students, type of institution/programs offered, the PSI's growth in enrolment over the last 10-15 years (depending on data avilability), available data on PSI's financial performance and combine with information related to IRCC study permits issued for the respective year.

- I would like to use this data on PSIs in an unsupervised learning model to find similar characteristics between institutions e.g. clusters (K means clustering) or PCA to identify the most distinctive variations between institutions.

- This may not be possible at the time of writing (November 3, 2024) but I would like to build a model which will predict future enrolment based on factors of the school such as:
  - Its student body composition (e.g. Domestic/international)
  - Its enrolment growth rate over 5 or 10 years (I am mindful of Covid impacting A/Y 20-21)
  - Its programming and courses offered, and diversity of these
  - Other features TBC
 The major thesis is that international students have been a major source of recruitment, revenue and expansion for reasons provided in Context below, and this will apply to some PSIs more than others. As enrolment is also a major predictor of revenue, if I am able to find from published Financial/Annual Reports on school websites, I can include this information.

Ultimately, I want this project to answer some business questions given the context below:
- **Which of Canada's PSIs should expect the most turbulence from recent federal IRCC changes?**
- **Are there underlying patterns to where or what types of schools are most exposed?**
- On a personal level, I am an account manager in education technology, specifically working with post-secondary institutions. Are there any relationships between schools I work with and those most at risk here?

It also has some **economic questions** that would be interesting to answer:
- Has any growth in student enrolment been seen equally across programs? In other words, is Canada producing more engineers, creatives or scientists as well as business graduates (which is [the most common area of study](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3710001101))

## Context of the project

Canada's post-secondary institutions have become a political talking point in the last 3-5 years due to the increase in international student enrolment figures. Some have argued the extent of this and its concentration in some urban areas has contributed to Canada's cost of living for young people due to competition for housing and employment. This was addressed in January 2024 when IRCC's Minister Miller announced a cap on new international study permits to around 360,000 in 2024. This would be a decrease of about 35% from the number that was approved in 2023.
  - This refers to the number of *new, approved* applications. Existing students renewing their permits are exempt from the cap. Masters and Doctoral degree students are also exempt.
  - IRCC [reports data on monthly issued study permits by province](https://open.canada.ca/data/en/dataset/90115b00-f9b8-49e8-afa3-b4cff8facaee), which it categorises by Secondary or Less, Post-Secondary, Other Studies and Education level not stated.
  - Given that Primary, Secondary and Master's & Doctoral students are exempt from the cap (which I have assume are captured in Other Studies), I used the Post Secondary Figure in the data for 2023 total, which is 526,860 multiplied by 0.65 to get 342,459. I am not certain how to make up the 21,541 gap between this number and the 364,000 quoted by Miller, other than having a slight buffer for variance (21,549 is about 6% of 364,000)

A position held by PSIs is that many provincial governments have cut grants and funding to their post-secondary institutions in recent years even as enrolment has increased. This is exacerbated in some provinces such as Ontario, where a freeze on tuition fees charged to Domestic students (Canadian Citizens, Permanent Residents and Refugees/Protected Persons) has existed since 2019. The response by PSIs has been to increase the number of international students where no such fee cap exists to cover a funding shortfall.


## Data Sources:

Data are taken from Excel spreadsheets from various federal and provincial websites, and in some cases the institution's own websites:

- [IRCC Data on study permit holders](https://open.canada.ca/data/en/dataset/90115b00-f9b8-49e8-afa3-b4cff8facaee)

- [Ontario MCU College Data](https://data.ontario.ca/dataset/college-enrolment )
 
- [Minister Miller Jan 2024](https://www.canada.ca/en/immigration-refugees-citizenship/news/2024/01/canada-to-stabilize-growth-and-decrease-number-of-new-international-student-permits-issued-to-approximately-360000-for-2024.html ) - International student cap.

- [Minister Miller April 2024](https://www.canada.ca/en/immigration-refugees-citizenship/news/2024/04/minister-miller-issues-statement-on-international-student-allocations-for-provinces-and-territories.html) - Provincial/territorial allocations of student permits.

- Information on programs of study: [Statistics Canada](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3710001101)


## Notes on data cleaning:

### MCU University enrolment
- Numbers less than 10 are NA

### MCU College enrolment
**Initial feature engineering of % by status was performed in Excel before importing into a notebook by Pandas dataframe by reading Excel**.

- Numbers less than 10 are NA to protect privacy. 
    - My action: I will replace * or NA with 5 to aid calculations and provide some estimate between 0-9

- I checked the multiple tabs of the excel workbook e.g. both age and gender to confirm the total enrolment numbers agree (for example, that the sum of all age demographics that counted enrolment and all gender options were in agreement). Age and Gender tend to align with some slight discrepancies of 5-10 in some schools

- Some discrepancies of 5-10 students when comparing total enrolment in a given year by Age or Gender vs Status. This amounts to around 0.2-0.5% of the total figures in most case
    - E.g. Centennial College 22-23 Enrolment by Gender was 21687 Full-time, it is 21695 in the numbers from Status. The difference of 8 divided by 21687 is 0.04% but we might expect some discrepancy as high as 0.5% with smaller schools

- Seneca 22-23 has 7613 of Unknown status out of 27000 - where are they from? Is this some stream of enrolment where that information wasn’t gathered? 
    - The % international students at Seneca in 2022-23 was 51% but due to this large Unknown category, it may be more.
    - Seneca did not have a field for Aboriginal students

- Cité Collégiale had no Aboriginal category so I used Other to assume that it included Aboriginal.

- Loyalist did not have a category for Study Permit holders in 2022-23, it did have Other which had 5152 respondents. Other was a category in some other Colleges with around 5 or 10 respondents at most. I assumed Study permit holders fell under this category at Loyalist

- Humber College had 11.3% in Other category despite having exhaustive categories for other status which many colleges did not. It’s not clear what status specifically these students had.



### IRCC study permits 15-24
- Between 0 and 5 are -- and all numbers are rounded to the nearest multiple of 5. 
- The data finished in August 2024 so 2024 has Q1, Q2 and two-thirds of Q3, with no Q4 available.
- I found data looking at 2004-Q1 2016 (legacy data) and some of the numbers do not agree, e.g. Ontario 2015 is about 1000 more in the new dataset than the legacy data, and legacy does not specify which study permit the holder had e.g. primary/secondary, Post-secondary, Other studies. This looks like it is around a 1-2% error.
- My actions:
    - I will delete the secondary and education not stated - the focus of this project is on the post-secondary environment, and ‘other studies’ isn’t clear whether it counts PhD and Master’s or if that is captured in the Post Secondary permit. For now it stays.
    - The month-by-month data has -- indicating 0-5, but those often aggregate and round to 5 or a multiple in the quarterly number, which is what I used to sum the post-secondary and other permits. Instead of filling every -- with 2.5 or 3, just taking the aggregated multiple of 5 at the quarterly level means I have only rounded once rather than potentially multiple times.
    - I will create a SUM function for each of the cells rather than the manual values entered in the raw data



## Important context: 

IRCC

Which category of study permit is being referred to?
- “International students” we usually mean post-secondary (not K-12) is this actually true? What about Masters or Doctoral studies?
    - Miller Jan 22 Statement “for 2024 the cap is expected to result in 360,000 approved permits, a decrease of 35% from 2023.” Master’s and Doctoral studies are not affected by the cap
        - 2023 total approved Post-Secondary study permits was 526,860 —> 0.65 * 526,800 = 342,420 not 360,000
        - 2023 total approved Post-Secondary plus Other Studies permits was 572,320 —> 0.65 * 372,008. But Other Studies likely refers to Masters and Doctoral studies, so we will assume Post Secondary without Other Studies is the cap being referred to.

    - Miller April 5, 2024 statement: “Some international students are exempt from the cap, such as primary and secondary school students and master’s or doctoral degree students. IRCC deducted the estimated volume of these groups (140,000 based on 2023 data) from the 2024 target number of approved study permits
        - The 2023 IRCC data on the website has around 150,000 in Secondary or less and Other Studies (assumed Masters or Doctoral). 
        - Confirmed - ‘Post secondary’ permit does not include Master’s or Doctoral, graduate certificates are likely post secondary but need to confirm.
