import os
import base64
import asyncio
import aiohttp

from loguru import logger 
from datetime import datetime, timedelta

github_token = os.getenv("GITHUB_TOKEN")
repo_owner = os.getenv("GITHUB_REPOSITORY_OWNER")
repo_name = os.getenv("GITHUB_REPOSITORY_NAME")

async def fetch_commit_date(session, repo_owner, repo_name):
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/commits'
    headers = {
        "Authorization": f"token {github_token}"
    }
    async with session.get(url, headers=headers) as response:
        data = await response.json()
        return data[0]['commit']['author']['date']

async def update_commit(session, repo_owner, repo_name, github_token, current_file_sha):
    commit_date = datetime.utcnow().strftime("%Y-%m-%d")
    commit_content = f"Commit date: {commit_date}"
    encoded_content = base64.b64encode(commit_content.encode('utf-8')).decode('utf-8')

    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/keep-alive'
    headers = {
        "Authorization": f"token {github_token}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "message": "Auto commit",
        "content": encoded_content,
        "committer": {
            "name": "Auto Commit Bot",
            "email": "bot@example.com"
        },
        "sha": current_file_sha 
    }

    async with session.put(url, headers=headers, json=data) as response:
        if response.status == 200:
            logger.info("Auto commit successful")
        else:
            logger.error(f"Failed to create commit. Status code: {response.status}, Message: {await response.text()}")

async def auto_commit():
    try:
        async with aiohttp.ClientSession() as session:
            last_commit_date = await fetch_commit_date(session, repo_owner, repo_name)
            last_commit_date = datetime.strptime(last_commit_date, "%Y-%m-%dT%H:%M:%SZ")

            current_date = datetime.utcnow()

            if current_date - last_commit_date > timedelta(days=30):
                response = await session.get(f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/keep-alive', headers={"Authorization": f"token {github_token}"})
                current_file_sha = (await response.json())['sha']

                await update_commit(session, repo_owner, repo_name, github_token, current_file_sha)
            else:
                logger.warning("No need commit")

    except Exception as e:
        logger.error(f"Error: {e.__class__.__name__} - {str(e)}")
