# replace:
# - bot-function-name
# - your-telegram-bot-bucket
gcloud functions deploy bot-function-name \
    --region=europe-west3 \
    --allow-unauthenticated \
    --entry-point=hook_bot \
    --ingress-settings=all \
    --memory=256MB \
    --runtime=python37 \
    --stage-bucket=your-telegram-bot-bucket \
    --timeout=540s \
    --env-vars-file=env.cloudfunction.yml \
    --max-instances=1 \
    --trigger-http \
    --verbosity=warning