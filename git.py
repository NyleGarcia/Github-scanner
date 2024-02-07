import csv
import json
import os.path
import string
from datetime import date
from datetime import datetime
import requests

key = ''
ORG = 'xyz'

today = str(date.today().strftime('%m-%d-%Y') )

def getRepoCount(ORG,key):
    url = "https://api.github.com/orgs/{ORG}".format(ORG = ORG)

    payload={}
    headers = {
    'Authorization': 'token {TOKEN}'.format(TOKEN = key)
    }

    response = requests.request("GET", url, headers=headers, data=payload).json()
    print(response["total_private_repos"])
    return response["total_private_repos"]


def getRepos(ORG,key,pages):

    repos = []
    
    for page in range(1,pages+1):
        print(page)
        url = "https://api.github.com/orgs/{ORG}/repos?per_page=100&page={PAGE}".format(ORG = ORG,PAGE = page)
        payload={}
        headers = {
        'Authorization': 'token {TOKEN}'.format(TOKEN = key)
        }

        response = requests.request("GET", url, headers=headers, data=payload).json()

        for repo in response:
            repos.append([repo["name"],repo['description'],repo['created_at'][:-10],repo['updated_at'][:-10],repo['pushed_at'][:-10],repo['language'],getLastCommitAuthor(ORG,repo["name"],key)])
    
    return repos

def writeCSV(values,name,headers):
    with open('{NAME}.csv'.format(NAME=name), mode='w') as file:
        file = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        file.writerow(headers)

        for value in values:
            file.writerow(value)


def getRepoInfo(ORG,repo,key):

    info = []
    url = "https://api.github.com/repos/{ORG}/{REPO}/stats/commit_activity".format(ORG=ORG,REPO=repo[0])
    print(repo[0])
    payload={}
    headers = {
    'Authorization': 'token {TOKEN}'.format(TOKEN = key)
    }
    try:
        response = requests.request("GET", url, headers=headers, data=payload).json()

        for week in response:
            if week['total'] > 0:
                info.append([repo[0],getDate(week['week']),week['total']])

        return info
    except Exception as e:
            return []
def getDate(timestamp):
    
    ts = int(timestamp)
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')

def getLastCommitAuthor(ORG,repo,key):
    url = "https://api.github.com/repos/{ORG}/{REPO}/commits?per_page=1".format(ORG = ORG,REPO = repo)

    payload={}
    headers = {
    'Authorization': 'token {TOKEN}'.format(TOKEN = key)
    }

    response = requests.request("GET", url, headers=headers, data=payload).json()
    
    for commit in response:
        try:
            return commit['author']['login']
        except Exception as e:
            return "None Found"
        

def main():

    pages = int(getRepoCount(ORG,key)/100)+1
    repos = getRepos(ORG,key,pages)
    writeCSV(repos,"Repos-"+today,['Repo Name', 'Description','Created Date',"Updated Date",'Pushed Date', 'Language','Last Commit Author'])
    repoInfo=[]
    for repo in repos:
        for info in getRepoInfo(ORG,repo,key):
            repoInfo.append(info)

    writeCSV(repoInfo,"Repos-Info-"+today,['Repo Name', 'Week of','# of Commits'])




if __name__ == '__main__':
    main()
