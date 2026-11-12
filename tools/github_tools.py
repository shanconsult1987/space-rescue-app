import json
import subprocess


def run_gh(arguments):

    result = subprocess.run(
        ["gh"] + arguments,
        capture_output=True,
        text=True,
        check=True
    )

    return result.stdout


def get_issue(repo, issue_number):

    output = run_gh([
        "issue",
        "view",
        str(issue_number),
        "--repo",
        repo,
        "--json",
        "number,title,body,state,url,labels"
    ])

    return json.loads(output)


def list_issues(repo):

    output = run_gh([
        "issue",
        "list",
        "--repo",
        repo,
        "--json",
        "number,title,state,labels"
    ])

    return json.loads(output)


def create_issue_comment(repo, issue_number, comment):

    run_gh([
        "issue",
        "comment",
        str(issue_number),
        "--repo",
        repo,
        "--body",
        comment
    ])

    return {
        "success": True,
        "message": "Comment created"
    }