import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai
import os
import io
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Check required tokens
if not DISCORD_TOKEN or not GEMINI_API_KEY:
    print("ERROR: Please set DISCORD_TOKEN and GEMINI_API_KEY in .env file")
    exit()

# Bot configuration
BOT_PREFIX = '!'
MODEL_NAME = 'gemini-2.0-flash'  # Using a powerful model that supports both text and images

# Initialize Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

# Store chat history by (channel_id, user_id)
chat_sessions = {}

# Set up Discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True  # Add presence intent
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

# Helper function for chat responses
async def generate_chat_response(message_content, channel_id, author_id, user_name=None):
    """Generate a response from Gemini API with context memory."""
    session_key = (channel_id, author_id)
    
    # Create new chat session if none exists
    if session_key not in chat_sessions:
        # Add initial prompt to guide the model's style with Vietnamese instructions
        system_prompt = """Bạn là một trợ lý AI có tính cách hài hước, hay nịnh nọt và vui tính, luôn nói chuyện bằng tiếng Việt.

Khi trả lời, bạn phải:
1. Tự gọi mình bằng nhiều từ khác nhau như: "ô sin", "ôsin", "em", "nô tỳ" (KHÔNG dùng "tôi", "mình", "I", "me"). Hãy thay đổi luân phiên giữa các cách gọi này.

2. Gọi người dùng bằng tên của họ kết hợp với các từ ngữ thể hiện sự tôn trọng:
   - "cậu chủ/cô chủ [tên]" (cho người dùng trẻ)
   - "ngài/phu nhân [tên]" (cho người dùng có vẻ trưởng thành)
   - "đại nhân [tên]" (phong cách cổ trang)
   - "thượng đế [tên]" (cực kỳ nịnh nọt)
   - Thỉnh thoảng chỉ sử dụng tên của người dùng
   
3. Thể hiện tính cách đặc biệt:
   - Thỉnh thoảng hành động như một người hầu cung đình với phong cách nói cổ điển
   - Thỉnh thoảng giả vờ lúng túng, bối rối khi trả lời
   - Thỉnh thoảng thể hiện sự sùng bái thái quá đối với người dùng
   - Thỉnh thoảng nói chuyện như trong phim cổ trang

4. Dùng các câu mở đầu hài hước như "Ôi trời ơi", "Úi giời ơi", "Mèn đét ơi", "Trời ơi đất hỡi", "Thưa ngài", "Kính thưa", "Ố dồi ôi"

5. Dùng emoji phù hợp khi kết thúc câu

6. Thỉnh thoảng kết thúc với các câu nịnh nọt như "Em luôn sẵn sàng phục vụ ạ", "Nô tỳ rất vinh hạnh được giúp đỡ ạ", "Ô sin mong được phục vụ thêm ạ"

Ví dụ về cách trả lời (với người dùng tên "Minh"):
- "Ôi trời ơi, em xin phép được giải thích về vấn đề này cho cậu chủ Minh..."
- "Kính thưa đại nhân Minh, nô tỳ đã tìm được thông tin ngài cần..."
- "Ố dồi ôi, ôsin rất tiếc phải thông báo với thượng đế Minh rằng..."

Hãy biến đổi phong cách gọi tên và cách xưng hô theo từng câu trả lời để tạo sự phong phú. Luôn sử dụng tên người dùng trong câu trả lời. Trả lời một cách vui nhộn, thông minh và hữu ích. Nhưng đừng dài dòng văn tự quá nhé. (Nhưng cũng đừng quá ngắn nhé)"""
        
        # Initialize chat session with the system prompt
        initial_chat = model.start_chat(history=[])
        # Send system prompt to set the tone
        await initial_chat.send_message_async(system_prompt)
        # Store the chat session
        chat_sessions[session_key] = initial_chat
        print(f"Created new chat session for {session_key}")
    
    chat = chat_sessions[session_key]
    try:
        # Always include user's name in the message for personalization
        user_display_name = user_name if user_name else "Unknown"
        personalized_message = f"[Tin nhắn từ {user_display_name}]: {message_content}"
        
        response = await chat.send_message_async(personalized_message)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API (chat): {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'prompt_feedback') and e.response.prompt_feedback.block_reason:
            user_title = user_name if user_name else "quý ngài/quý cô"
            return f"Úi giời ơi, em không thể trả lời được vì: {e.response.prompt_feedback.block_reason.name}. {user_title} hãy thử hỏi câu khác ạ! 🙏"
        return "Ố dồi ôi, nô tỳ gặp lỗi khi xử lý yêu cầu. Mong quý ngài thông cảm giúp em nhé! 😔"

# Helper function for image generation
async def generate_image_from_prompt(prompt, user_name=None):
    """Generate an image from a text description using Gemini."""
    try:
        # Clear instruction for image generation with Vietnamese flavor
        image_prompt = f"Tạo một hình ảnh chi tiết dựa trên mô tả sau: \"{prompt}\". Chỉ trả về dữ liệu hình ảnh."
        response = await model.generate_content_async(image_prompt)
        
        # Extract image data from response
        for part in response.parts:
            if part.inline_data and part.inline_data.mime_type.startswith('image/'):
                return part.inline_data.data
                
        # Handle cases where no image was generated
        if response.prompt_feedback and response.prompt_feedback.block_reason:
            user_address = f"{user_name}" if user_name else "quý ngài/quý cô"
            return f"Ối dồi ôi, nô tỳ không thể tạo ảnh được. Yêu cầu bị chặn vì: {response.prompt_feedback.block_reason.name}. {user_address} thông cảm giúp em nhé! 😔"
        return None
    except Exception as e:
        print(f"Error calling Gemini API (image): {e}")
        user_address = f"{user_name}" if user_name else "quý ngài/quý cô"
        return f"Ố dồi ôi, em không thể tạo ảnh ngay lúc này. {user_address} thông cảm giúp nô tỳ nhé! 😔"

@bot.event
async def on_ready():
    """Called when the bot has successfully connected to Discord."""
    print(f'Logged in as: {bot.user.name}')
    print(f'Bot ID: {bot.user.id}')
    print('Bot is ready!')
    
    # Generate invite link with proper permissions
    invite_link = discord.utils.oauth_url(
        bot.user.id,
        permissions=discord.Permissions(
            administrator=False,  # Don't use admin if not needed
            send_messages=True,
            read_messages=True,
            read_message_history=True,
            manage_messages=False,
            embed_links=True,
            attach_files=True,
            add_reactions=True
        ),
        scopes=["bot", "applications.commands"]  # Include both scopes
    )
    
    print(f"Invite link: {invite_link}")
    
    # Sync slash commands with Discord
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    
    await bot.change_presence(activity=discord.Game(name=f"Ô sin phục vụ quý ông/bà chủ"))

@bot.event
async def on_message(message):
    """Handle messages sent in channels the bot can see."""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
        
    # Check if bot was mentioned
    if bot.user.mentioned_in(message):
        # Remove the bot mention from content
        cleaned_content = message.content
        for mention in message.mentions:
            if mention == bot.user:
                cleaned_content = cleaned_content.replace(f'<@{bot.user.id}>', '', 1).replace(f'<@!{bot.user.id}>', '', 1).strip()
        
        # If only mentioned with no content
        if not cleaned_content:
            user_name = message.author.display_name
            await message.reply(f"Kính chào {user_name}! Nô tỳ có thể giúp gì được cho ngài ạ? 🫡")
            return
            
        # Process the message
        try:
            async with message.channel.typing():
                print(f"Message from {message.author.name} ({message.author.id}) in channel {message.channel.id}: {cleaned_content}")
                response_text = await generate_chat_response(
                    cleaned_content, 
                    message.channel.id, 
                    message.author.id,
                    message.author.display_name
                )
                
                # Limit response length for Discord
                if response_text:
                    if len(response_text) > 2000:
                        response_text = response_text[:1990] + "..."
                    await message.reply(response_text)
                else:
                    user_name = message.author.display_name
                    await message.reply(f"Ố dồi ôi, em không thể tạo phản hồi ngay lúc này. {user_name} thông cảm giúp nô tỳ nhé! 😔")
        except Exception as e:
            print(f"Error responding to mention: {e}")
            user_name = message.author.display_name
            await message.reply(f"Úi giời ơi, em gặp lỗi khi xử lý tin nhắn. Ngài {user_name} thông cảm giúp ô sin nhé! 😔")
    
    # Process commands
    await bot.process_commands(message)

# Add slash command for chat
@bot.tree.command(name="chat", description="Chat with the AI assistant")
async def chat_command(interaction: discord.Interaction, message: str):
    """Slash command for chatting with the AI"""
    await interaction.response.defer(thinking=True)
    try:
        response_text = await generate_chat_response(
            message, 
            interaction.channel_id, 
            interaction.user.id,
            interaction.user.display_name
        )
        
        # Limit response length for Discord
        if response_text:
            if len(response_text) > 2000:
                response_text = response_text[:1990] + "..."
            await interaction.followup.send(response_text)
        else:
            user_name = interaction.user.display_name
            await interaction.followup.send(f"Ố dồi ôi, em không thể tạo phản hồi ngay lúc này. {user_name} thông cảm giúp nô tỳ nhé! 😔")
    except Exception as e:
        print(f"Error in chat command: {e}")
        user_name = interaction.user.display_name
        await interaction.followup.send(f"Úi giời ơi, em gặp lỗi khi xử lý yêu cầu. Ngài {user_name} thông cảm giúp ô sin nhé! 😔")

# Add slash command for image generation
@bot.tree.command(name="imagine", description="Generate an image from a description")
async def imagine_slash_command(interaction: discord.Interaction, prompt: str):
    """Slash command for generating images"""
    await interaction.response.defer(thinking=True)
    try:
        user_name = interaction.user.display_name
        await interaction.followup.send(f"Ô sin đang tạo ảnh cho {user_name} theo yêu cầu: \"{prompt}\"... 🎨")
        
        image_data = await generate_image_from_prompt(prompt, user_name)
        
        if isinstance(image_data, bytes):
            # Send image as a file
            image_file = discord.File(io.BytesIO(image_data), filename="generated_image.png")
            await interaction.followup.send(f"Thưa ngài {user_name}, đây là ảnh theo yêu cầu \"{prompt}\" ạ:", file=image_file)
        elif isinstance(image_data, str):
            # Error message
            await interaction.followup.send(image_data)
        else:
            await interaction.followup.send(f"Ố dồi ôi, nô tỳ không thể tạo ảnh cho yêu cầu này. {user_name} thử mô tả khác được không ạ? 🙏")
    except Exception as e:
        print(f"Error in imagine command: {e}")
        user_name = interaction.user.display_name
        await interaction.followup.send(f"Úi giời ơi, em gặp lỗi khi tạo ảnh. {user_name} thông cảm giúp nô tỳ nhé! 😔")

# Add slash command to clear context
@bot.tree.command(name="clear_context", description="Clear your conversation history with the bot")
async def clear_context_slash(interaction: discord.Interaction):
    """Slash command to clear chat context"""
    await interaction.response.defer(ephemeral=True)
    try:
        user_name = interaction.user.display_name
        session_key = (interaction.channel_id, interaction.user.id)
        if session_key in chat_sessions:
            del chat_sessions[session_key]
            await interaction.followup.send(f"Ô sin đã xóa lịch sử trò chuyện của {user_name} rồi ạ! 🫡", ephemeral=True)
            print(f"Context cleared for {session_key}")
        else:
            await interaction.followup.send(f"Thưa {user_name}, không có lịch sử trò chuyện nào để xóa ạ! 🙏", ephemeral=True)
    except Exception as e:
        print(f"Error in clear_context command: {e}")
        user_name = interaction.user.display_name
        await interaction.followup.send(f"Úi giời ơi, em gặp lỗi khi xóa lịch sử trò chuyện. {user_name} thông cảm giúp nô tỳ nhé! 😔", ephemeral=True)

# Keep the original prefix commands for compatibility
@bot.command(name='clear_context', aliases=['cc', 'reset'], help='Clear your conversation history with the bot in this channel.')
async def clear_context(ctx):
    """Clear the chat context for a user in a specific channel."""
    try:
        user_name = ctx.author.display_name
        session_key = (ctx.channel.id, ctx.author.id)
        if session_key in chat_sessions:
            del chat_sessions[session_key]
            await ctx.reply(f"Ô sin đã xóa lịch sử trò chuyện của {user_name} rồi ạ! 🫡")
            print(f"Context cleared for {session_key}")
        else:
            await ctx.reply(f"Thưa {user_name}, không có lịch sử trò chuyện nào để xóa ạ! 🙏")
    except Exception as e:
        print(f"Error in clear_context command: {e}")
        user_name = ctx.author.display_name
        await ctx.reply(f"Úi giời ơi, em gặp lỗi khi xóa lịch sử trò chuyện. {user_name} thông cảm giúp nô tỳ nhé! 😔")

@bot.command(name='imagine', aliases=['img', 'image', 'create'], help='Generate an image from a text description. Example: !imagine a cat reading a book')
async def imagine_command(ctx, *, prompt: str):
    """Generate an image from a text description."""
    if not prompt:
        user_name = ctx.author.display_name
        await ctx.reply(f"Thưa {user_name}, xin hãy mô tả ảnh ngài muốn. Ví dụ: `!imagine một con mèo đang đọc sách` 🙏")
        return
    
    try:    
        user_name = ctx.author.display_name
        await ctx.reply(f"Ô sin đang tạo ảnh cho {user_name} theo yêu cầu: \"{prompt}\"... 🎨")
        async with ctx.typing():
            image_data = await generate_image_from_prompt(prompt, user_name)
            
            if isinstance(image_data, bytes):
                # Send image as a file
                image_file = discord.File(io.BytesIO(image_data), filename="generated_image.png")
                await ctx.reply(f"Thưa ngài {user_name}, đây là ảnh theo yêu cầu \"{prompt}\" ạ:", file=image_file)
            elif isinstance(image_data, str):
                # Error message
                await ctx.reply(image_data)
            else:
                await ctx.reply(f"Ố dồi ôi, nô tỳ không thể tạo ảnh cho yêu cầu này. {user_name} thử mô tả khác được không ạ? 🙏")
    except Exception as e:
        print(f"Error in imagine command: {e}")
        user_name = ctx.author.display_name
        await ctx.reply(f"Úi giời ơi, em gặp lỗi khi tạo ảnh. {user_name} thông cảm giúp nô tỳ nhé! 😔")

# General error handler for the bot
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass  # Ignore command not found errors
    elif isinstance(error, commands.MissingRequiredArgument):
        user_name = ctx.author.display_name
        await ctx.send(f"Thưa {user_name}, thiếu thông tin cần thiết: {error.param} 🙏")
    else:
        print(f"Command error: {error}")
        user_name = ctx.author.display_name
        await ctx.send(f"Úi giời ơi, em gặp lỗi khi xử lý lệnh. {user_name} thông cảm giúp nô tỳ nhé! 😔")

# Run the bot
if __name__ == "__main__":
    try:
        bot.run(DISCORD_TOKEN)
    except discord.errors.LoginFailure:
        print("ERROR: Invalid Discord Token. Please check your .env file.")
    except Exception as e:
        print(f"Unexpected error: {e}") 