from flask import Flask, render_template, redirect, url_for
import requests
import json
from datetime import datetime
import markdown

app = Flask(__name__)

token = "add your token here"

@app.template_filter("md")
def md(input):
  return markdown.markdown(input)

@app.template_filter("strptime")
def strptime(input):
  return datetime.strptime(input, "%Y-%m-%dT%H:%M:%SZ").strftime("%b %d, %Y")

@app.route("/")
def home():
  return(f'<head><link rel="stylesheet" href="/static/style.css"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>bathub</title></head><body><h1>bathub</h1><p>simple, no JS github frontend. just replace github.com with the bathub url and replace all question marks (?) with forward slashes (/).</p><p><a href="/godotengine">an example user</a></p><hr><p>made by <a href="https://tilde.team/~flat">flat</a> as a learning project, no promises of quality.</body>')

@app.route("/<user>")
def userpage(user):
  req = requests.get(f'https://api.github.com/users/{user}', headers={"Authorization": f"Bearer {token}"}).text
  req = json.loads(req)
  return render_template("user.html", name=req["name"], login=req["login"], avatar_url=req["avatar_url"], html_url=req["html_url"], bio=req["bio"], followers=req["followers"], following=req["following"], repos_url=req["repos_url"], public_repos=req["public_repos"], user=user, created_at=strptime(req["created_at"]))

@app.route("/<user>/tab=repositories")
def reporedirect(user):
  return redirect(url_for("repos", page=1, user=user))

@app.route("/<user>/<repo>/releases")
def releaseredirect(user, repo):
  return redirect(url_for("releases", user=user, repo=repo, page=1))

@app.route("/<user>/<repo>/tags")
def tagredirect(user, repo):
  return redirect(url_for("tags", user=user, repo=repo, page=1))

@app.route("/<user>/page=<int:page>&tab=repositories")
def repos(user, page):
  req = requests.get(f'https://api.github.com/users/{user}/repos?page={page}', headers={"Authorization": f"Bearer {token}"}).text
  req = json.loads(req)
  return render_template("repos.html", user=user, req=req, page=page)

@app.route("/<user>/<repo>")
def repo(user, repo):
  req = requests.get(f'https://api.github.com/repos/{user}/{repo}', headers={"Authorization": f"Bearer {token}"}).text
  req = json.loads(req)
  readme = requests.get(f'https://raw.githubusercontent.com/{user}/{repo}/master/README.md', headers={"Authorization": f"Bearer {token}"})
  readme = markdown.markdown(readme.text) if readme.status_code == 200 else "nope"
  return render_template("repo.html", user=user, repo=repo, req=req, readme=readme)

@app.route("/<user>/<repo>/releases/page=<int:page>")
def releases(user, repo, page):
  req = requests.get(f'https://api.github.com/repos/{user}/{repo}/releases?page={page}', headers={"Authorization": f"Bearer {token}"}).text
  req = json.loads(req)
  return render_template("releases.html", user=user, repo=repo, req=req, page=page)

@app.route("/<user>/<repo>/tags/page=<int:page>")
def tags(user, repo, page):
  req = requests.get(f'https://api.github.com/repos/{user}/{repo}/tags?page={page}', headers={"Authorization": f"Bearer {token}"}).text
  req = json.loads(req)
  return render_template("tags.html", user=user, repo=repo, req=req, page=page)

@app.route("/<user>/<repo>/tree/<branch>")
def treeroot(user, repo, branch):
  req = requests.get(f'https://api.github.com/repos/{user}/{repo}/git/trees/{branch}', headers={"Authorization": f"Bearer {token}"}).text
  req = json.loads(req)
  return render_template("tree.html", user=user, repo=repo, branch=branch, req=req)

@app.route("/<user>/<repo>/tree/<branch>/<path:path>")
def tree(user, repo, branch, path):
  req = requests.get(f'https://api.github.com/repos/{user}/{repo}/git/trees/{branch}', headers={"Authorization": f"Bearer {token}"}).text
  req = json.loads(req)
  for tree in req["tree"]:
    if tree["type"] == "tree" and tree["path"] == path.split("/")[0]:
      sha = tree["sha"]
      break
  for subpath in path.split("/"):
    req = requests.get(f'https://api.github.com/repos/{user}/{repo}/git/trees/{sha}', headers={"Authorization": f"Bearer {token}"}).text
    req = json.loads(req)
    for tree in req["tree"]:
      if tree["type"] == tree and tree["path"] == path.split("/")[len(path.split("/")) - 1]:
        sha = tree["sha"]
        print(sha)
        req = requests.get(f'https://api.github.com/repos/{user}/{repo}/git/trees/{sha}', headers={"Authorization": f"Bearer {token}"}).text
        req = json.loads(req)
      elif tree["type"] == "tree" and tree["path"] in path.split("/"):
        sha = tree["sha"]
  return render_template("tree.html", user=user, repo=repo, branch=branch, req=req, path=path)
