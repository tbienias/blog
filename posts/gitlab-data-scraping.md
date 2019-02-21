# Scraping Data from GitLab using Python #

### 26/04/2018 ###

[GitLab](https://gitlab.com/) offers several functionalities for keeping track of project status. This article will explain how to gather data from GitLab. Here we will explain how-to gather all the meaningful data GitLab provides for us.

## [](#gathering-data-easily)Gathering Data Easily
### [](#gitlab-api)GitLab API
Since we're lazy we aim for gathering data the easy way. GitLab provides a splendid [API](https://docs.gitlab.com/ee/api/) for querying all kinds of project-related data. A quick scan of their documentation states that we're gonna use `GET` requests for accessing data through GitLab's REST-API. 
Anyways, we want an even simpler solution so [googling](https://www.google.com/search?hl=en&as_q=gitlab+python) for _gitlab python_ spits out [this little gem](https://github.com/python-gitlab/python-gitlab). _python-gitlab_ is a Python wrapper for GitLab - what do we want more?! Let's see how easy it is to gather some data for evaluation purposes.
### [](#python-gitlab)python-gitlab
For evaluating this library we want to print arbitrary project names of publicly available projects hosted on GitLab. 
So first things first - install _python-gitlab_:

`$ pip install python-gitlab`

According to _python-gitlab_'s [documentation](http://python-gitlab.readthedocs.io/en/stable/index.html) we can acquire so-called manager objects which provide methods to act on GitLab ressources. Well, enough theory for now - let's get our feet wet and hack a little script together that authenticates us on the GitLab server, gets a list of 20 publicly available projects and prints the name of each.

#### [](#print_project_names)print_project_names.py
```python
import gitlab


def main():
    auth_token = 'YOUR_AUTH_TOKEN'

    gl = gitlab.Gitlab('https://gitlab.com', private_token=auth_token)
    gl.auth()

    projects = gl.projects.list(visibility='public')
    for project in projects:
        print(project.name)


if __name__ == "__main__":
    main()

```

Calling the script by `$ python gitlab_count_public_repos.py` prints this little list for us:
```
twitter-saver-deploy
vim-config
VirtualCPU
vagrant
VillageManagement
cmocka
ShareDatClient
UnityShaders
ts3statistics
LowPolyPlanets
cartel
PythonExperiments
Releases
SendingToProcess
CSharp-FSMFramework
NetworkHRM
dotin-school-files
AOGLFW
cricket-me-divi
Matrix
```
This was ez af just in case you're asking me!

## [](#gathering-data-the-real-deal)Gathering Data - The Real Deal
### [](#what-data)What Data?
We need to determine what data we want to get from our neat GitLab project. 
So let's create a table where we state what data we want and why we want it:

| What            | Why         
|:----------------|:------------------|
| [Project Members](http://python-gitlab.readthedocs.io/en/stable/gl_objects/projects.html#project-members) | To persist nicknames and real names for linking all the other data to people
| [Commits](http://python-gitlab.readthedocs.io/en/stable/gl_objects/commits.html)         | This enables us to explore Git activities   
| [Issues](http://python-gitlab.readthedocs.io/en/stable/gl_objects/issues.html)          | Since we use GitLab Issues for assigning tasks to devs we also need this 
| [Notes](http://python-gitlab.readthedocs.io/en/stable/gl_objects/projects.html?#notes)           | Notes (comments) belong to an issue and hold important data such as tracked time
| [Milestones](http://python-gitlab.readthedocs.io/en/stable/gl_objects/milestones.html)           | Issues are linked to milestones in our project
| [Labels](http://python-gitlab.readthedocs.io/en/stable/gl_objects/labels.html)           | Labels serve semantic purposes and split the Agile Board into columns

Hopefully these thingies are enough to create some meaningful statistics out of their data - so keep it comming now!

### [](#lets-script)Let's Script
First we need to consider in which format we save our data. For the first iteration it should be absolutely sufficient to save our data using the CSV file format.

So let's take care of our imports:
#### [](#build_database)build_database.py
```python
import gitlab
import csv
```
As seen [above](#gitlab_count_public_repos) we get a list of objects for each entity we're querying. 
For the sake of simplicity we need to create a method that takes a list and a name as inputs and pumps the objects into a CSV file named after (guess what) the inputted name:
```python
def build_csv(object_list, csv_name):
    keys = object_list[0].attributes.keys()
    with open(csv_name + '.csv', 'w') as f:
        w = csv.DictWriter(f, keys)
        w.writeheader()
        for object in object_list:
            w.writerow(object.attributes)
```
Next, in our `main` we need to do some setup as seen earlier:
```python
def main():
    auth_token = 'YOUR_AUTH_TOKEN'
    project_id = -1

    # Establish GitLab connection and get project
    gl = gitlab.Gitlab('https://gitlab.com', private_token=auth_token)
    gl.auth()
    project = gl.projects.get(project_id)
```
So now we get to the real greedy part of our tiny script - data!!! We begin with the project members:
```python
    # Build project member database
    members = project.members.list(all=True)
    build_csv(members, 'members')
```
Time to handle issues:
```python
    # Build issue database
    issues = project.issues.list(all=True)
    build_csv(issues, 'issues')
```
Gathering all the notes related to an issue requires some extra work since we need to iterate over all issues and extract the corresponding notes:
```python
    # Build note database
    notes = list()
    for issue in issues:
        issue_notes = issue.notes.list(all=True)
        notes += issue_notes  # Merge lists instead of appending
    build_csv(notes, 'notes')
```
To make a long story short we scrape the milestones, labels and commits in the same fashion as we did above and call `main`:
```python
    # Build milestone database
    milestones = project.milestones.list(all=True)
    build_csv(milestones, 'milestones')

    # Build label database
    labels = project.labels.list(all=True)
    build_csv(labels, 'labels')

    # Build commit database
    commits = project.commits.list(all=True)
    build_csv(commits, 'commits')


if __name__ == "__main__":
    main()
```
By running the script with `$ python build_gitlab_database.py` we end up with six CSV files containing all the data in plain text - mission accomplished!

## [](#conclusion)Conclusion
In this post we have shown how to collect project-related data from GitLab without much effort. We used _python-gitlab_ to accomplish the task and ended up with data being saved in CSV files. 
In a future blog post we will take a look at our data and compute some statistics.
The `build_database.py` script is included in [this repository](https://gitlab.com/JACKSONMEISTER/gitlab-data).