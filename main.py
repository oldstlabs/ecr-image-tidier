import os
import re

import boto3

REGISTRY_ID = os.getenv('REGISTRY_ID', None)


def get_all_repositories(ecr):
    """ Get all the existing repositories in ECR
        This isn't a very scalable way of doing this, but AWS only let you
        have 10 at a time, and it's still pretty fast so <shrug emoticon>
    """

    repositories = []
    kwargs = {}
    next_token = True

    # This is paging through the list - nextToken is the page id
    while next_token:
        response = ecr.describe_repositories(registryId=REGISTRY_ID, **kwargs)
        repositories += response['repositories']
        next_token = response.get('nextToken', None)
        kwargs = {'nextToken': next_token}

    return repositories


def get_all_images(ecr, repo_name):
    """ Get all the existing images for this repo in ECR
        This isn't a very scalable way of doing this, but AWS only let you
        have 10 at a time, and it's still pretty fast so <shrug emoticon>
    """

    images = []
    kwargs = {}
    next_token = True

    # This is paging through the list - nextToken is the page id
    while next_token:
        response = ecr.describe_images(
            registryId=REGISTRY_ID,
            repositoryName=repo_name,
            **kwargs
        )
        images += response['imageDetails']
        next_token = response.get('nextToken', None)
        kwargs = {'nextToken': next_token}

    return images


def tidy_images(event, context):

    if not REGISTRY_ID:
        print('Please configure an environment variable with your ECR registry id')
    else:
        # Create an ecr client
        ecr = boto3.client('ecr')

        for repo in get_all_repositories(ecr):
            to_delete = []
            images = get_all_images(ecr, repo['repositoryName'])
            # We only care about the repos that are getting crazy big
            if len(images) > 100:
                print('%s has more than 100 images' % repo['repositoryName'])
                # Sort and reverse so the newest are first
                sorted_images = list(reversed(sorted(images, key=lambda x: x['imagePushedAt'])))
                # Keep the top 100
                for image in sorted_images[100:]:
                    for tag in image.get('imageTags', []):
                        if tag == 'latest':  # i.e. this is on live
                            print("Saw but won't delete", image['imageTags'])
                            break
                        elif re.search('[a-zA-Z]', tag):  # i.e. we probably write a comment
                            print("Saw but won't delete", image['imageTags'])
                            break
                    else:
                        print('Delete', image.get('imageTags'), image['imagePushedAt'])
                        to_delete.append({
                            'imageDigest': image['imageDigest']
                        })

                if to_delete:
                    # Batch delete only takes 100 at a time
                    for i in range(0, len(to_delete), 100):
                        ecr.batch_delete_image(
                            registryId=REGISTRY_ID,
                            repositoryName=repo['repositoryName'],
                            imageIds=to_delete[i:i+100]
                        )


if __name__ == '__main__':
    tidy_images(None, None)
