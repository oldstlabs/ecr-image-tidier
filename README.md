# ECR Image Tidyer

A quick script designed to clean up your AWS ECR Repositories. These can only store 1000 images by default and they all cost money, and if you have a CI system like ours you quickly end up hitting that limit.

It keeps the most recent 100 images in each repository, along with those with the tag `latest` and indeed any with letters in the tag. This is because CIs usually produce numbered revisions, but gives you the opportunity to quickly stop something being deleted by adding an alphabetical tag.

Designed to run on AWS Lambda with Python 3.6. Simply set the `REGISTRY_ID` environment variable to that for your registry, and make sure it runs with a role with the appropriate permissions (`ecr:DescribeRepositories`, `ecr:DescribeImages`, `ecr:BatchDeleteImages`)

We run once a week to ensure we aren't holding too many images, but also to not delete any that people might still want to use.

(Tidyer as in something that tidies. Not tidier, which is what you end up with your ECR Repos being)
