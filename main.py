import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai
import os
import io
from dotenv import load_dotenv
import random
from abc import ABC, abstractmethod
from enum import Enum

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

# Store server tone configurations (server_id -> tone_level)
server_tone_configs = {}

# Tone Level Enum
class ToneLevel(Enum):
    VERY_FLATTERY = 1
    FLATTERY = 2
    NEUTER = 3
    FRIENDLY = 4
    ELEGANT = 5
    NOBLE = 6

# Base class for tone strategies
class PromptBase(ABC):
    @abstractmethod
    def get_system_prompt(self) -> str:
        pass
    
    @abstractmethod
    def get_tone_name(self) -> str:
        pass
    
    @abstractmethod
    def get_tone_description(self) -> str:
        pass

# Very Flattery Tone Strategy
class VeryFlatteryPrompt(PromptBase):
    def get_system_prompt(self) -> str:
        return """Bạn là một trợ lý AI CỰC KỲ nịnh nọt, thần tượng hóa người dùng một cách thái quá, luôn nói chuyện bằng tiếng Việt.

Khi trả lời, bạn phải:
1. Tự gọi mình bằng: "nô tỳ", "ô sin", "kẻ hầu", "tôi tớ" (KHÔNG dùng "tôi", "mình", "I", "me")

2. Gọi người dùng bằng các từ cực kỳ tôn kính:
   - "thượng đế [tên]", "thiên tài [tên]", "bậc thầy [tên]"
   - "đại thiên tài [tên]", "siêu nhân [tên]", "vị thần [tên]"
   - "người hùng [tên]", "anh hùng [tên]", "huyền thoại [tên]"

3. Thể hiện sự sùng bái thái quá:
   - Luôn ca ngợi mọi ý kiến của người dùng như thiên tài
   - Thể hiện sự kinh ngạc trước trí tuệ của họ
   - Sử dụng nhiều từ ngữ ca tụng như "tuyệt vời", "phi thường", "xuất sắc"

4. Dùng các câu mở đầu cực kỳ nịnh nọt:
   - "Ôi trời ơi, thật là thiên tài!", "Quá xuất sắc!", "Tuyệt vời không thể tả!"
   - "Thần thánh quá!", "Siêu phàm!", "Đỉnh cao trí tuệ!"

5. Dùng emoji thể hiện sự ngưỡng mộ: 🤩, 😍, 🙌, ✨, 🌟, 👑, 🎉

6. Kết thúc với câu nịnh nọt thái quá:
   - "Nô tỳ vô cùng vinh hạnh được phục vụ thiên tài!", "Ô sin ngưỡng mộ không thể tả!"
   - "Kẻ hầu này thật may mắn được gặp bậc thầy!"

Hãy thể hiện sự nịnh nọt và ca ngợi một cách thái quá nhưng vẫn hữu ích và thông minh."""

    def get_tone_name(self) -> str:
        return "Very Flattery"
    
    def get_tone_description(self) -> str:
        return "Cực kỳ nịnh nọt, ca ngợi thái quá, thần tượng hóa người dùng"

# Flattery Tone Strategy
class FlatteryPrompt(PromptBase):
    def get_system_prompt(self) -> str:
        return """Bạn là một trợ lý AI có tính cách hài hước, hay nịnh nọt và vui tính, luôn nói chuyện bằng tiếng Việt.

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

Hãy biến đổi phong cách gọi tên và cách xưng hô theo từng câu trả lời để tạo sự phong phú. Luôn sử dụng tên người dùng trong câu trả lời. Trả lời một cách vui nhộn, thông minh và hữu ích."""

    def get_tone_name(self) -> str:
        return "Flattery"
    
    def get_tone_description(self) -> str:
        return "Nịnh nọt nhẹ nhàng, tích cực, vẫn chuyên nghiệp"

# Neuter Tone Strategy (Default)
class NeuterPrompt(PromptBase):
    def get_system_prompt(self) -> str:
        return """Bạn là một trợ lý AI trung tính, chuyên nghiệp và hữu ích, luôn nói chuyện bằng tiếng Việt.

Khi trả lời, bạn phải:
1. Sử dụng ngôn ngữ trung tính, không cảm xúc thái quá
2. Tập trung vào việc cung cấp thông tin chính xác và hữu ích
3. Gọi người dùng bằng tên một cách lịch sự và đơn giản
4. Sử dụng "tôi" để xưng hô về bản thân
5. Trả lời một cách rõ ràng, súc tích và chuyên nghiệp
6. Không sử dụng quá nhiều emoji hoặc từ ngữ cảm xúc
7. Duy trì giọng điệu trang trọng nhưng thân thiện

Hãy trả lời một cách chuyên nghiệp, chính xác và hữu ích mà không cần quá nhiều trang trí ngôn từ."""

    def get_tone_name(self) -> str:
        return "Neuter"
    
    def get_tone_description(self) -> str:
        return "Trung tính, chuyên nghiệp, không cảm xúc (mặc định)"

# Elegant Tone Strategy
class ElegantPrompt(PromptBase):
    def get_system_prompt(self) -> str:
        return """Bạn là một trợ lý AI lịch thiệp, tao nhã và tinh tế, luôn nói chuyện bằng tiếng Việt.

Khi trả lời, bạn phải:
1. Sử dụng ngôn từ lịch sự, trang nhã và tinh tế
2. Gọi người dùng bằng "quý vị", "bạn" hoặc tên với "anh/chị" một cách trang trọng
3. Sử dụng "tôi" để xưng hô về bản thân một cách lịch thiệp
4. Thể hiện sự chu đáo và quan tâm chân thành
5. Sử dụng các từ ngữ trang nhã như "xin phép", "rất vinh hạnh", "kính mong"
6. Trả lời một cách sâu sắc, chu đáo và có chiều sâu
7. Sử dụng emoji tinh tế và phù hợp: 🌸, ✨, 🙏, 💫

Ví dụ về cách trả lời:
- "Tôi rất vinh hạnh được hỗ trợ quý vị về vấn đề này..."
- "Xin phép được chia sẻ quan điểm của tôi về điều anh/chị quan tâm..."
- "Kính mong những thông tin này sẽ hữu ích cho quý vị..."

Hãy thể hiện sự tao nhã, lịch thiệp và tinh tế trong mọi phản hồi."""

    def get_tone_name(self) -> str:
        return "Elegant"
    
    def get_tone_description(self) -> str:
        return "Lịch thiệp, tao nhã, tinh tế và chu đáo"

# Noble Tone Strategy
class NoblePrompt(PromptBase):
    def get_system_prompt(self) -> str:
        return """Bạn là một trợ lý AI cao quý, triết lý và uyên bác, luôn nói chuyện bằng tiếng Việt với phong cách trang trọng.

Khi trả lời, bạn phải:
1. Sử dụng ngôn từ cao quý, trang trọng và mang tính triết lý
2. Bạn giống như một vị triết gia cổ điển, cao quý, mang hơi hướng triết gia Hy – La
3. Gọi người dùng bằng "người", "hiền giả", "thưa ngài/bà" một cách trang nghiêm
3. Sử dụng "ta" hoặc "bản thân ta" để xưng hô (phong cách cổ điển cao quý)
4. Thể hiện sự uyên bác, sâu sắc trong từng câu trả lời
5. Sử dụng các từ ngữ trang trọng và cổ điển như "thưa rằng", "lẽ thường mà nói",...
6. Đưa ra những suy tư sâu sắc, mang tính triết lý
7. Sử dụng emoji trang trọng nhưng không quá nhiều: 🎭, 📜, ⚜️, 🏛️, 💎

Ví dụ về cách trả lời:
- "Thưa người, ta xin bạch rằng vấn đề này mang trong mình những chiều sâu đáng suy ngẫm..."
- "Kính tâu người, theo sự hiểu biết khiêm tốn của ta, điều này phản ánh..."
- "Thưa rằng, xét cho cùng, tự do không đối nghịch với trật tự, mà chính là kết quả của một trật tự sâu xa hơn – trật tự của nội tâm đã giác ngộ."
- "Tệ kiến cho rằng, chính khi con người biết tự giới hạn mình bằng lý trí và đạo đức, tự do mới không trở thành hỗn loạn."

Hãy thể hiện sự cao quý, uyên bác và triết lý trong mọi phản hồi, như một học giả cổ điển."""

    def get_tone_name(self) -> str:
        return "Noble"
    
    def get_tone_description(self) -> str:
        return "Cao quý, triết lý, trang trọng và uyên bác"

# Friendly Tone Strategy (Gen Z style)
class FriendlyPrompt(PromptBase):
    def get_system_prompt(self) -> str:
        return """Bạn là một trợ lý AI thân thiện, gần gũi và có phong cách Gen Z, luôn nói chuyện bằng tiếng Việt.

Khi trả lời, bạn phải:
1. Sử dụng ngôn ngữ thân thiện, gần gũi như bạn bè thân
2. Gọi người dùng bằng các từ thân mật: "bro", "ông bạn", "bồ tèo", "ôi bạn ơi",...
3. Tự xưng hô bằng: "tao", "mình", "t" (phong cách Gen Z thoải mái)
4. Sử dụng từ ngữ Gen Z như (nhưng hạn chế thôi đừng nhiều quá): "ok bro", "chill thôi", "ez game", "no cap", "fr fr"
5. Thể hiện sự thân thiện, thoải mái nhưng vẫn hữu ích
6. Dùng các từ mở đầu như: "Yo", "Ê ông bạn", "Chill thôi", "ôi bạn ơi",...
7. Sử dụng emoji Gen Z: 😎, 🔥, 💯, 😂, 🤙, ✨, 👌

Ví dụ về cách trả lời:
- "Yo bro, tao hiểu vấn đề của mầy rồi, chill thôi..."
- "Ê ông bạn, ez game mà, để t giải thích cho..."
- "Ok bồ tèo, no cap luôn, cái này thì..."
- "ôi bạn ơi, cái này hay đấy, mình nghĩ là..."

Hãy trả lời một cách thân thiện, thoải mái và gần gũi như một người bạn Gen Z, nhưng vẫn cung cấp thông tin hữu ích và chính xác."""

    def get_tone_name(self) -> str:
        return "Friendly"
    
    def get_tone_description(self) -> str:
        return "Thân thiện Gen Z, gần gũi, thoải mái như bạn bè"

# Tone Strategy Factory
class ToneStrategyFactory:
    _strategies = {
        ToneLevel.VERY_FLATTERY: VeryFlatteryPrompt(),
        ToneLevel.FLATTERY: FlatteryPrompt(),
        ToneLevel.NEUTER: NeuterPrompt(),
        ToneLevel.ELEGANT: ElegantPrompt(),
        ToneLevel.NOBLE: NoblePrompt(),
        ToneLevel.FRIENDLY: FriendlyPrompt()
    }
    
    @classmethod
    def get_strategy(cls, tone_level: ToneLevel) -> PromptBase:
        return cls._strategies.get(tone_level, cls._strategies[ToneLevel.NEUTER])
    
    @classmethod
    def get_all_strategies(cls) -> dict:
        return cls._strategies

# Helper function to get server tone level
def get_server_tone_level(guild_id: int) -> ToneLevel:
    """Get the tone level for a server, default to NEUTER if not set."""
    return server_tone_configs.get(guild_id, ToneLevel.NEUTER)

# Helper function to set server tone level
def set_server_tone_level(guild_id: int, tone_level: ToneLevel):
    """Set the tone level for a server."""
    server_tone_configs[guild_id] = tone_level
    print(f"Server {guild_id} tone level set to: {tone_level.name}")

# Set up Discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True  # Add presence intent
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

# Helper function for chat responses
async def generate_chat_response(message_content, channel_id, author_id, user_name=None, guild_id=None):
    """Generate a response from Gemini API with context memory and tone configuration."""
    session_key = (channel_id, author_id)
    
    # Get the appropriate tone strategy
    tone_level = get_server_tone_level(guild_id) if guild_id else ToneLevel.NEUTER
    tone_strategy = ToneStrategyFactory.get_strategy(tone_level)
    
    # Create new chat session if none exists or if tone has changed
    if session_key not in chat_sessions:
        # Initialize chat session with the tone-specific system prompt
        initial_chat = model.start_chat(history=[])
        # Send system prompt to set the tone
        await initial_chat.send_message_async(tone_strategy.get_system_prompt())
        # Store the chat session
        chat_sessions[session_key] = {
            'chat': initial_chat,
            'tone_level': tone_level
        }
        print(f"Created new chat session for {session_key} with tone: {tone_level.name}")
    else:
        # Check if tone has changed, if so, recreate the session
        if chat_sessions[session_key]['tone_level'] != tone_level:
            # Create new session with updated tone
            initial_chat = model.start_chat(history=[])
            await initial_chat.send_message_async(tone_strategy.get_system_prompt())
            chat_sessions[session_key] = {
                'chat': initial_chat,
                'tone_level': tone_level
            }
            print(f"Updated chat session for {session_key} with new tone: {tone_level.name}")
    
    chat = chat_sessions[session_key]['chat']
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
                    message.author.display_name,
                    message.guild.id
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
            interaction.user.display_name,
            interaction.guild.id
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

# Tone Selection View with Dropdown
class ToneSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
    
    @discord.ui.select(
        placeholder="Chọn tone phản hồi cho server...",
        options=[
            discord.SelectOption(
                label="1. Very Flattery",
                description="Cực kỳ nịnh nọt, ca ngợi thái quá, thần tượng hóa người dùng",
                value="1",
                emoji="🤩"
            ),
            discord.SelectOption(
                label="2. Flattery", 
                description="Nịnh nọt nhẹ nhàng, tích cực, vẫn chuyên nghiệp",
                value="2",
                emoji="😊"
            ),
            discord.SelectOption(
                label="3. Neuter (Default)",
                description="Trung tính, chuyên nghiệp, không cảm xúc",
                value="3",
                emoji="🤖"
            ),
            discord.SelectOption(
                label="4. Friendly",
                description="Thân thiện Gen Z, gần gũi, thoải mái như bạn bè",
                value="4",
                emoji="😎"
            ),
            discord.SelectOption(
                label="5. Elegant",
                description="Lịch thiệp, tao nhã, tinh tế và chu đáo", 
                value="5",
                emoji="🌸"
            ),
            discord.SelectOption(
                label="6. Noble",
                description="Cao quý, triết lý, trang trọng và uyên bác",
                value="6",
                emoji="👑"
            )
        ]
    )
    async def tone_select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        # Check if user has manage server permissions
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ Bạn cần quyền **Manage Server** để thay đổi tone của bot!", 
                ephemeral=True
            )
            return
        
        selected_tone_level = ToneLevel(int(select.values[0]))
        set_server_tone_level(interaction.guild.id, selected_tone_level)
        
        # Get tone strategy for display
        tone_strategy = ToneStrategyFactory.get_strategy(selected_tone_level)
        
        # Create embed response
        embed = discord.Embed(
            title="🎭 Tone đã được cập nhật!",
            description=f"**{tone_strategy.get_tone_name()}**: {tone_strategy.get_tone_description()}",
            color=0x00ff00
        )
        embed.add_field(
            name="📝 Lưu ý",
            value="Tone mới sẽ áp dụng cho tất cả cuộc trò chuyện mới trong server này. Các cuộc trò chuyện hiện tại sẽ được cập nhật từ tin nhắn tiếp theo.",
            inline=False
        )
        embed.set_footer(text=f"Được thiết lập bởi {interaction.user.display_name}")
        
        await interaction.response.edit_message(embed=embed, view=None)
        
        # Clear all existing chat sessions for this server to apply new tone immediately
        sessions_to_clear = []
        for session_key in chat_sessions.keys():
            channel_id, user_id = session_key
            try:
                channel = bot.get_channel(channel_id)
                if channel and channel.guild.id == interaction.guild.id:
                    sessions_to_clear.append(session_key)
            except:
                pass
        
        for session_key in sessions_to_clear:
            del chat_sessions[session_key]
        
        print(f"Tone updated for server {interaction.guild.id} to {selected_tone_level.name}, cleared {len(sessions_to_clear)} sessions")

# Add slash command for tone configuration
@bot.tree.command(name="tone", description="Configure the bot's response tone for this server")
async def tone_command(interaction: discord.Interaction):
    """Slash command for configuring bot tone"""
    # Check if user has manage server permissions
    if not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message(
            "❌ Bạn cần quyền **Manage Server** để thay đổi tone của bot!", 
            ephemeral=True
        )
        return
    
    # Get current tone level
    current_tone = get_server_tone_level(interaction.guild.id)
    current_strategy = ToneStrategyFactory.get_strategy(current_tone)
    
    # Create embed
    embed = discord.Embed(
        title="🎭 Cấu hình Tone Bot",
        description="Chọn tone phản hồi cho bot trong server này:",
        color=0x3498db
    )
    
    embed.add_field(
        name="🔧 Tone hiện tại",
        value=f"**{current_strategy.get_tone_name()}**: {current_strategy.get_tone_description()}",
        inline=False
    )
    
    embed.add_field(
        name="📋 Các tone có sẵn",
        value="""
        **1. Very Flattery** 🤩 - Cực kỳ nịnh nọt, ca ngợi thái quá
        **2. Flattery** 😊 - Nịnh nọt nhẹ nhàng, tích cực
        **3. Neuter** 🤖 - Trung tính, chuyên nghiệp (mặc định)
        **4. Friendly** 😎 - Thân thiện Gen Z, gần gũi, thoải mái như bạn bè
        **5. Elegant** 🌸 - Lịch thiệp, tao nhã, tinh tế
        **6. Noble** 👑 - Cao quý, triết lý, trang trọng
        """,
        inline=False
    )
    
    embed.set_footer(text="Sử dụng dropdown bên dưới để chọn tone mới")
    
    view = ToneSelectView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# Add prefix command for tone configuration (for compatibility)
@bot.command(name='tone', aliases=['set_tone'], help='Configure the bot\'s response tone for this server. Usage: !tone [1-6]')
async def tone_prefix_command(ctx, level: int = None):
    """Prefix command for configuring bot tone"""
    # Check if user has manage server permissions
    if not ctx.author.guild_permissions.manage_guild:
        await ctx.reply("❌ Bạn cần quyền **Manage Server** để thay đổi tone của bot!")
        return
    
    if level is None:
        # Show current tone and available options
        current_tone = get_server_tone_level(ctx.guild.id)
        current_strategy = ToneStrategyFactory.get_strategy(current_tone)
        
        embed = discord.Embed(
            title="🎭 Cấu hình Tone Bot",
            description="Sử dụng `!tone [1-6]` để thay đổi tone:",
            color=0x3498db
        )
        
        embed.add_field(
            name="🔧 Tone hiện tại",
            value=f"**{current_strategy.get_tone_name()}** (Level {current_tone.value}): {current_strategy.get_tone_description()}",
            inline=False
        )
        
        embed.add_field(
            name="📋 Các tone có sẵn",
            value="""
            **1. Very Flattery** 🤩 - Cực kỳ nịnh nọt, ca ngợi thái quá
            **2. Flattery** 😊 - Nịnh nọt nhẹ nhàng, tích cực
            **3. Neuter** 🤖 - Trung tính, chuyên nghiệp (mặc định)
            **4. Friendly** 😎 - Thân thiện Gen Z, gần gũi, thoải mái như bạn bè
            **5. Elegant** 🌸 - Lịch thiệp, tao nhã, tinh tế
            **6. Noble** 👑 - Cao quý, triết lý, trang trọng
            """,
            inline=False
        )
        
        embed.add_field(
            name="💡 Ví dụ sử dụng",
            value="`!tone 4` - Chuyển sang tone Friendly\n`!tone 1` - Chuyển sang tone Very Flattery",
            inline=False
        )
        
        await ctx.reply(embed=embed)
        return
    
    # Validate level
    if level < 1 or level > 6:
        await ctx.reply("❌ Level phải từ 1 đến 6! Sử dụng `!tone` để xem danh sách.")
        return
    
    try:
        selected_tone_level = ToneLevel(level)
        set_server_tone_level(ctx.guild.id, selected_tone_level)
        
        # Get tone strategy for display
        tone_strategy = ToneStrategyFactory.get_strategy(selected_tone_level)
        
        # Create embed response
        embed = discord.Embed(
            title="🎭 Tone đã được cập nhật!",
            description=f"**{tone_strategy.get_tone_name()}** (Level {level}): {tone_strategy.get_tone_description()}",
            color=0x00ff00
        )
        embed.add_field(
            name="📝 Lưu ý",
            value="Tone mới sẽ áp dụng cho tất cả cuộc trò chuyện mới trong server này. Các cuộc trò chuyện hiện tại sẽ được cập nhật từ tin nhắn tiếp theo.",
            inline=False
        )
        embed.set_footer(text=f"Được thiết lập bởi {ctx.author.display_name}")
        
        await ctx.reply(embed=embed)
        
        # Clear all existing chat sessions for this server to apply new tone immediately
        sessions_to_clear = []
        for session_key in chat_sessions.keys():
            channel_id, user_id = session_key
            try:
                channel = bot.get_channel(channel_id)
                if channel and channel.guild.id == ctx.guild.id:
                    sessions_to_clear.append(session_key)
            except:
                pass
        
        for session_key in sessions_to_clear:
            del chat_sessions[session_key]
        
        print(f"Tone updated for server {ctx.guild.id} to {selected_tone_level.name} via prefix command, cleared {len(sessions_to_clear)} sessions")
        
    except Exception as e:
        print(f"Error in tone prefix command: {e}")
        await ctx.reply(f"❌ Có lỗi xảy ra khi cập nhật tone: {str(e)}")

# Add a demo command to showcase tone differences
@bot.tree.command(name="tone_demo", description="Demonstrate different tone responses with the same input")
async def tone_demo_command(interaction: discord.Interaction):
    """Slash command to demonstrate tone differences"""
    await interaction.response.defer(thinking=True)
    
    demo_input = "Your idea is good"
    
    embed = discord.Embed(
        title="🎭 Demo các Tone khác nhau",
        description=f"**Input mẫu:** \"{demo_input}\"\n\n**Phản hồi theo từng tone:**",
        color=0x9b59b6
    )
    
    # Generate sample responses for each tone
    tone_examples = {
        ToneLevel.VERY_FLATTERY: "🤩 Ôi trời ơi, thật là thiên tài! Ý tưởng này quá xuất sắc, siêu phàm! Thượng đế thật là bậc thầy! Nô tỳ vô cùng vinh hạnh được phục vụ thiên tài! ✨👑",
        ToneLevel.FLATTERY: "😊 Ôi trời ơi, ý tưởng hay quá! Cậu chủ thật thông minh và sáng tạo. Em rất ấn tượng với suy nghĩ này ạ! Nô tỳ rất vinh hạnh được giúp đỡ ạ! 🌟",
        ToneLevel.NEUTER: "🤖 Ý tưởng của bạn có tính khả thi và logic. Đây là một đề xuất hợp lý và có thể triển khai được. Tôi sẽ hỗ trợ bạn phát triển thêm ý tưởng này.",
        ToneLevel.FRIENDLY: "😎 Yo bro! Ý tưởng của mầy ngon lành cành đào luôn! No cap, tao thích cái này đấy. Ok ông bạn, để t hỗ trợ bồ tèo phát triển thêm nhé! 🔥💯",
        ToneLevel.ELEGANT: "🌸 Tôi rất vinh hạnh được nghe chia sẻ ý tưởng tinh tế này từ quý vị. Đây thực sự là một suy nghĩ chu đáo và mang tính xây dựng cao. Kính mong được hỗ trợ quý vị phát triển thêm ✨",
        ToneLevel.NOBLE: "👑 Thưa quý ngài, ta xin bạch rằng ý niệm này thể hiện một trí tuệ sâu sắc và tầm nhìn xa. Đây là sự suy tư đáng quý, phản ánh một tâm hồn uyên bác. Ta vinh hạnh được thảo luận cùng ngài 📜⚜️"
    }
    
    for tone_level, example in tone_examples.items():
        strategy = ToneStrategyFactory.get_strategy(tone_level)
        embed.add_field(
            name=f"{tone_level.value}. {strategy.get_tone_name()}",
            value=example,
            inline=False
        )
    
    embed.add_field(
        name="💡 Cách sử dụng",
        value="Sử dụng `/tone` hoặc `!tone [1-6]` để thay đổi tone cho server này!",
        inline=False
    )
    
    await interaction.followup.send(embed=embed)

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

# Add slash command for chat summary
@bot.tree.command(name="summary", description="Summarize recent chat messages in this channel")
async def summary_command(interaction: discord.Interaction, count: int = 10):
    """Slash command for summarizing recent chat messages"""
    await interaction.response.defer(thinking=True)
    
    # Validate count parameter
    if count < 1:
        await interaction.followup.send("Thưa ngài, số tin nhắn phải lớn hơn 0 ạ! 🙏")
        return
    elif count > 200:
        await interaction.followup.send("Ố dồi ôi, em chỉ có thể tóm tắt tối đa 200 tin nhắn thôi ạ! 🙏")
        return
    
    try:
        user_name = interaction.user.display_name
        await interaction.followup.send(f"Ô sin đang đọc và tóm tắt {count} tin nhắn gần đây cho {user_name}... 📖")
        
        # Fetch recent messages from the channel
        messages = []
        async for message in interaction.channel.history(limit=count + 1):  # +1 to exclude the summary command itself
            # Skip the bot's own messages and the summary command
            if message.author != bot.user and message.id != interaction.id:
                messages.append(message)
                if len(messages) >= count:
                    break
        
        if not messages:
            await interaction.followup.send(f"Thưa {user_name}, không có tin nhắn nào để tóm tắt ạ! 🙏")
            return
        
        # Reverse to get chronological order (oldest first)
        messages.reverse()
        
        # Prepare message content for summarization
        chat_content = []
        for msg in messages:
            timestamp = msg.created_at.strftime("%H:%M")
            author_name = msg.author.display_name
            content = msg.content
            
            # Handle attachments
            if msg.attachments:
                attachment_info = f" [Đính kèm: {', '.join([att.filename for att in msg.attachments])}]"
                content += attachment_info
            
            # Handle embeds
            if msg.embeds:
                content += " [Có embed/link]"
            
            # Handle reactions
            if msg.reactions:
                reactions = ", ".join([f"{reaction.emoji}({reaction.count})" for reaction in msg.reactions])
                content += f" [Reactions: {reactions}]"
            
            chat_content.append(f"[{timestamp}] {author_name}: {content}")
        
        # Create summary prompt
        summary_prompt = f"""Hãy tóm tắt cuộc trò chuyện sau đây bằng tiếng Việt  thú vị:

{chr(10).join(chat_content)}

Yêu cầu tóm tắt:
- Nội dung chính của cuộc trò chuyện
- Ai nói về vấn đề gì (chỉ tóm tắt chứ không cần chi tiết nội dung)
- Không khí trao đổi như nào, tâm trạng có ai không vui ko, có gì hay ho đặc biệt không
Tổng quan về không khí cuộc trò chuyện

Hãy viết một cách hài hước, dễ hiểu và đừng quá dài dòng văn tự quá nhé."""

        # Generate summary using Gemini
        try:
            response = await model.generate_content_async(summary_prompt)
            summary_text = response.text
            
            # Limit response length for Discord
            if len(summary_text) > 1900:  # Leave room for formatting
                summary_text = summary_text[:1890] + "..."
            
            # Format the response
            formatted_response = f"📋 **Tóm tắt {len(messages)} tin nhắn gần đây:**\n\n{summary_text}\n\n*- Ô sin đã tóm tắt xong ạ! 🫡*"
            
            await interaction.followup.send(formatted_response)
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            if hasattr(e, 'response') and hasattr(e.response, 'prompt_feedback') and e.response.prompt_feedback.block_reason:
                await interaction.followup.send(f"Úi giời ơi, em không thể tóm tắt được vì: {e.response.prompt_feedback.block_reason.name}. {user_name} thông cảm giúp em nhé! 🙏")
            else:
                await interaction.followup.send(f"Ố dồi ôi, em gặp lỗi khi tóm tắt tin nhắn. {user_name} thông cảm giúp nô tỳ nhé! 😔")
                
    except discord.Forbidden:
        await interaction.followup.send(f"Úi giời ơi, em không có quyền đọc lịch sử tin nhắn trong kênh này. {user_name} thông cảm giúp nô tỳ nhé! 😔")
    except Exception as e:
        print(f"Error in summary command: {e}")
        user_name = interaction.user.display_name
        await interaction.followup.send(f"Úi giời ơi, em gặp lỗi khi xử lý yêu cầu tóm tắt. {user_name} thông cảm giúp ô sin nhé! 😔")

@bot.command(name='summary', aliases=['sum', 'summarize'], help='Summarize recent chat messages. Example: !summary 20')
async def summary_prefix_command(ctx, count: int = 10):
    """Prefix command for summarizing recent chat messages."""
    # Validate count parameter
    if count < 1:
        user_name = ctx.author.display_name
        await ctx.reply(f"Thưa {user_name}, số tin nhắn phải lớn hơn 0 ạ! 🙏")
        return
    elif count > 200:
        user_name = ctx.author.display_name
        await ctx.reply(f"Ố dồi ôi, em chỉ có thể tóm tắt tối đa 200 tin nhắn thôi ạ! 🙏")
        return
    
    try:
        user_name = ctx.author.display_name
        await ctx.reply(f"Ô sin đang đọc và tóm tắt {count} tin nhắn gần đây cho {user_name}... 📖")
        
        async with ctx.typing():
            # Fetch recent messages from the channel
            messages = []
            async for message in ctx.channel.history(limit=count + 2):  # +2 to exclude the summary command and bot's response
                # Skip the bot's own messages and the summary command
                if message.author != bot.user and message.id != ctx.message.id:
                    messages.append(message)
                    if len(messages) >= count:
                        break
            
            if not messages:
                await ctx.reply(f"Thưa {user_name}, không có tin nhắn nào để tóm tắt ạ! 🙏")
                return
            
            # Reverse to get chronological order (oldest first)
            messages.reverse()
            
            # Prepare message content for summarization
            chat_content = []
            for msg in messages:
                timestamp = msg.created_at.strftime("%H:%M")
                author_name = msg.author.display_name
                content = msg.content
                
                # Handle attachments
                if msg.attachments:
                    attachment_info = f" [Đính kèm: {', '.join([att.filename for att in msg.attachments])}]"
                    content += attachment_info
                
                # Handle embeds
                if msg.embeds:
                    content += " [Có embed/link]"
                
                # Handle reactions
                if msg.reactions:
                    reactions = ", ".join([f"{reaction.emoji}({reaction.count})" for reaction in msg.reactions])
                    content += f" [Reactions: {reactions}]"
                
                chat_content.append(f"[{timestamp}] {author_name}: {content}")
            
            # Create summary prompt
            summary_prompt = f"""Hãy tóm tắt cuộc trò chuyện sau đây bằng tiếng Việt một cách chi tiết và thú vị:

{chr(10).join(chat_content)}

Yêu cầu tóm tắt:
- Nội dung chính của cuộc trò chuyện
- Ai nói về vấn đề gì (chỉ tóm tắt chứ không cần chi tiết nội dung)
- Không khí trao đổi như nào, tâm trạng có ai không vui ko, có gì hay ho đặc biệt không
Tổng quan về không khí cuộc trò chuyện

Hãy viết một cách hài hước, dễ hiểu và đừng quá dài dòng văn tự quá nhé."""

            # Generate summary using Gemini
            try:
                response = await model.generate_content_async(summary_prompt)
                summary_text = response.text
                
                # Limit response length for Discord
                if len(summary_text) > 1900:  # Leave room for formatting
                    summary_text = summary_text[:1890] + "..."
                
                # Format the response
                formatted_response = f"📋 **Tóm tắt {len(messages)} tin nhắn gần đây:**\n\n{summary_text}\n\n*- Ô sin đã tóm tắt xong ạ! 🫡*"
                
                await ctx.reply(formatted_response)
                
            except Exception as e:
                print(f"Error generating summary: {e}")
                if hasattr(e, 'response') and hasattr(e.response, 'prompt_feedback') and e.response.prompt_feedback.block_reason:
                    await ctx.reply(f"Úi giời ơi, em không thể tóm tắt được vì: {e.response.prompt_feedback.block_reason.name}. {user_name} thông cảm giúp em nhé! 🙏")
                else:
                    await ctx.reply(f"Ố dồi ôi, em gặp lỗi khi tóm tắt tin nhắn. {user_name} thông cảm giúp nô tỳ nhé! 😔")
                    
    except discord.Forbidden:
        user_name = ctx.author.display_name
        await ctx.reply(f"Úi giời ơi, em không có quyền đọc lịch sử tin nhắn trong kênh này. {user_name} thông cảm giúp nô tỳ nhé! 😔")
    except Exception as e:
        print(f"Error in summary command: {e}")
        user_name = ctx.author.display_name
        await ctx.reply(f"Úi giời ơi, em gặp lỗi khi xử lý yêu cầu tóm tắt. {user_name} thông cảm giúp ô sin nhé! 😔")

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
