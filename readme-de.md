# EffiClean - Cleaning Schedule Dash Application for short term rentals
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/jonatasemidio/multilanguage-readme-pattern/blob/master/README.md)
[![ger](https://img.shields.io/badge/lang-ger-green.svg)](https://github.com/jonatasemidio/multilanguage-readme-pattern/blob/master/README.md)

Welcome to EffiClean, a lightweight tool designed to help property managers and cleaning teams efficiently schedule cleaning tasks for short-term rental properties. This tool currently integrates with **Smoobu**, a popular booking management system, to generate optimized cleaning schedules and ensure a seamless guest experience.

## **Project Goals**

EffiClean simplifies the planning and execution of cleaning schedules by:
1. **Optimizing Cleaning Dates**: Suggests the most efficient days (i.e. the least amount of trips to site) for cleaning across multiple properties at a single site to minimize workload and maximize turnaround time.
2. **Streamlining Communication**: Provides cleaning staff with clear, detailed schedules with all nescessary information.
3. **Customizable Options**:
   - Adjust the maximum number of uncleaned days.
   - Filter specific subsets of apartments
4. **Guest Preparation Assistance**:
   - Displays the number of guests for the next booking, ensuring cleaning staff prepare the correct number of beds and amenities.

---

## **Features**

1. **Seamless Integration with Smoobu**:
   - Automatically fetch booking data, including check-in and check-out dates.

2. **Intelligent Scheduling**:
   - Generate cleaning plans that balance workload and prioritize reducing the number of visits of cleaning staff.

3. **Customizable Parameters**:
   - Set rules such as the maximum number of uncleaned days.

4. **Staff-Friendly Outputs**:
   - Provide clear, actionable schedules as color-coded PDFs to cleaning staff, ensuring they have all necessary details to prepare properties efficiently.

5. **Guest-Specific Preparation**:
   - Highlight the number of guests staying in the next booking, enabling staff to prepare the correct number of beds and other essentials.
---

## **Getting Started**

First, you need to generate an API key for Smoodu. Further information can be found here [link to smoodu].
You can build the app yourself to run locally or use the Dockerfile to run it on a server / docker provider of your choice.  

1. Clone this repository
```bash
   git clone https://github.com/smoky1337/efficlean.git
```
2. Install dependencies  

Efficlean is build on Python 3.9, but there should be no issues using any newer version. 
```bash
  cd cleaning-plan-optimizer
  pip install -r requirements.txt
```
3. Create `config.json` by editing `config_template.json` and saving it  as `config.json` with your API-Key  


4. Test the application by using
````bash
python app.py
````

## Current Status
🚧 Under Development  
EffiClean is in its early development phase. While it’s free to use for testing and feedback purposes, redistribution or modification beyond publicly contributing is not permitted until further notice.


## Feedback and Contribution
We welcome feedback to help improve the project! If you encounter any issues or have feature suggestions, please open an issue in this repository. Contributions will be accepted soon. 