#!/bin/bash

# Monitor CloudFormation Stack Progress
# This script monitors the stack creation progress and shows the final outputs

set -e

STACK_NAME="aws-propuestas-v3-mcp-servers"
AWS_REGION="us-east-1"

echo "🔍 Monitoring CloudFormation stack: ${STACK_NAME}"
echo "Region: ${AWS_REGION}"
echo ""

# Function to get stack status
get_stack_status() {
    aws cloudformation describe-stacks \
        --stack-name ${STACK_NAME} \
        --region ${AWS_REGION} \
        --query 'Stacks[0].StackStatus' \
        --output text 2>/dev/null || echo "STACK_NOT_FOUND"
}

# Function to show latest events
show_latest_events() {
    echo "📋 Latest stack events:"
    aws cloudformation describe-stack-events \
        --stack-name ${STACK_NAME} \
        --region ${AWS_REGION} \
        --max-items 5 \
        --query 'StackEvents[*].[Timestamp,LogicalResourceId,ResourceStatus,ResourceStatusReason]' \
        --output table
    echo ""
}

# Function to show stack outputs
show_stack_outputs() {
    echo "🎯 Stack Outputs:"
    aws cloudformation describe-stacks \
        --stack-name ${STACK_NAME} \
        --region ${AWS_REGION} \
        --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue,Description]' \
        --output table
    echo ""
}

# Monitor loop
while true; do
    STATUS=$(get_stack_status)
    echo "⏰ $(date): Stack Status = ${STATUS}"
    
    case ${STATUS} in
        "CREATE_COMPLETE")
            echo "✅ Stack creation completed successfully!"
            show_stack_outputs
            echo "🚀 Ready to build and push Docker images!"
            echo "Run: ./scripts/build-and-push-images.sh"
            break
            ;;
        "CREATE_FAILED"|"ROLLBACK_COMPLETE"|"ROLLBACK_FAILED")
            echo "❌ Stack creation failed!"
            show_latest_events
            echo "Check the AWS Console for detailed error information."
            exit 1
            ;;
        "CREATE_IN_PROGRESS")
            show_latest_events
            echo "⏳ Waiting 30 seconds before next check..."
            sleep 30
            ;;
        "STACK_NOT_FOUND")
            echo "❌ Stack not found!"
            exit 1
            ;;
        *)
            echo "⚠️  Unknown status: ${STATUS}"
            show_latest_events
            sleep 30
            ;;
    esac
done
