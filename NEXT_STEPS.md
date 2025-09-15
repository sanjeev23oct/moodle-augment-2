# 🚀 Next Steps After Docker Push Success

Congratulations! Your Docker image has been successfully pushed to Snowflake. Here's what to do next:

## Step 1: Deploy Python Service in Snowflake

1. **Open Snowflake Snowsight** in your browser:
   - Go to: https://app.snowflake.com/plqnvnr/sg37212/

2. **Open a new worksheet** and copy-paste the entire contents of:
   ```
   snowflake_service_deployment.sql
   ```

3. **Run the SQL script** - this will:
   - Create a compute pool for your Python application
   - Deploy your Python AI service
   - Set up the endpoints

4. **IMPORTANT**: After running the script, note down the **endpoint URL** from this command:
   ```sql
   SHOW ENDPOINTS IN SERVICE moodle_app.public.python_ai_service;
   ```
   
   The URL will look something like:
   ```
   https://xyz123-python-ai-endpoint.snowflakecomputing.app
   ```

## Step 2: Test Your Python Service

Run this test in Snowflake (replace `<your-endpoint-url>` with the actual URL):

```sql
SELECT SYSTEM$SEND_REQUEST('GET', '<your-endpoint-url>/health', {}, {});
```

You should get a response showing your service is healthy.

## Step 3: Install Moodle Plugin

1. **Zip your Moodle plugin**:
   - Create a zip file of the `local_ai_question_gen` folder

2. **Install in Moodle**:
   - Go to Site Administration > Plugins > Install Plugins
   - Upload the zip file
   - Follow the installation wizard

## Step 4: Configure Moodle Plugin

1. **Go to plugin settings**:
   - Site Administration > Plugins > Local plugins > AI Question Generator

2. **Configure the endpoint**:
   - Set the Python Service URL to your endpoint URL from Step 1
   - Configure any API keys (OpenAI, Gemini) if you have them

## Step 5: Test the Integration

1. **Navigate to the plugin**:
   - Go to `/local/ai_question_gen/index.php` in your Moodle

2. **Test question generation**:
   - Enter some sample content
   - Select question type
   - Generate questions using AI

## 🔧 Troubleshooting

If something doesn't work:

1. **Check service status**:
   ```sql
   SELECT SYSTEM$GET_SERVICE_STATUS('moodle_app.public.python_ai_service');
   ```

2. **Check service logs**:
   ```sql
   SELECT SYSTEM$GET_SERVICE_LOGS('moodle_app.public.python_ai_service', 0, 'python-ai-container', 100);
   ```

3. **Verify endpoint is accessible**:
   - Try accessing `<your-endpoint-url>/health` in a browser

## 📞 Need Help?

Refer to the complete deployment guide in `docs/requirement.md` for detailed troubleshooting steps.

---

**You're almost there! Just follow these steps and your AI-powered Moodle plugin will be live! 🎉**
