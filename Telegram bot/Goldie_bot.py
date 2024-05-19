from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import asyncio

# Define your bot token
TOKEN = "7108076179:AAGZzcta6XXVMO6hob6bKaUebjywgsUkH9k"

# Define the verification status globally
verification_status = {}

# Define the command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Welcome to GoldieCoin Community")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """
        /start -> Welcome to the GoldieCoin
        /help -> You can reach out our support for help
        /website -> About the GoldieCoin
        """
    )

async def join_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the user provided an invite link
    if len(context.args) == 0:
        await update.message.reply_text("Please provide an invite link.")
        return
    
    invite_link = context.args[0]
    
    try:
        # Try to join the group using the invite link
        chat = await context.bot.join_chat(invite_link)
        await update.message.reply_text(f"Successfully joined the group {chat.title}.")
    except Exception as e:
        await update.message.reply_text(f"Failed to join the group: {str(e)}")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Contact @ShibaPlat for any help")

async def website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("goldiecoin.ai")

# Define a function to handle new users and start verification
async def new_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.effective_chat.restrict_member(
             update.message.from_user.id,
             permissions=ChatPermissions(can_send_messages=False)
         )
        if member.id not in verification_status:
            verification_status[member.id] = {"chat_id": update.message.chat.id}
            keyboard = [[InlineKeyboardButton("Click to Verify", callback_data="verify")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                update.message.chat.id,
                f"Welcome {member.full_name}! To verify that you are human, please click the button below:",
                reply_markup=reply_markup
            )

# Define a function to handle the verification button click
async def verify_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id in verification_status:
        permissions = ChatPermissions(can_send_messages=True)
        await context.bot.restrict_chat_member(
            verification_status[user_id]["chat_id"],
            user_id,
            permissions=permissions
        )
        await query.answer("You have been verified! Welcome to the GoldieCoin Community!")
        await query.message.delete()
        #del verification_status[user_id]
    del verification_status[user_id]
# Create the Application and pass it your bot's token
application = Application.builder().token(TOKEN).build()

# Add the command handlers to the application
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("menu", menu))
application.add_handler(CommandHandler("help", help))
application.add_handler(CommandHandler("website", website))
application.add_handler(CommandHandler("join", join_group))
application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_user))
application.add_handler(CallbackQueryHandler(verify_button))

# Run the bot
application.run_polling()