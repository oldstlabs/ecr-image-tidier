# ECR Image Tidier

A quick script designed to clean up your AWS ECR Repositories. These can only store 1000 images by default and they all cost money, and if you have a CI system like ours you quickly end up hitting that limit.

It keeps the most recent 100 images in each repository, along with those with the tag `latest` and indeed any with letters in the tag. This is because CIs usually produce numbered revisions, but gives you the opportunity to quickly stop something being deleted by adding an alphabetical tag.

Designed to run on AWS Lambda with Python 3.6. There's no need for any extra modules, just create a new Python 3.6 function in the Lambda console and copy and paste the code. If you're not sure how, [the AWS Tutorial takes you through the main steps](http://docs.aws.amazon.com/lambda/latest/dg/get-started-create-function.html).

Simply set the `REGISTRY_ID` environment variable to that for your registry, and make sure it runs with a role with the appropriate permissions (`ecr:DescribeRepositories`, `ecr:DescribeImages`, `ecr:BatchDeleteImages`). If you're not too sure on how to add specific permissions to an IAM role, you can create a new one with the `AWSLambdaFullAccess` and `AmazonEC2ContainerRegistryFullAccess` policies, and this will work (but means it has more access than strictly necessary)

We run once a week to ensure we aren't holding too many images, but also to not delete any that people might still want to use.
