#Import Pandas for reading CSV files and discord for API integration.
import pandas as pd
import discord

#Set intents for discord bot
intents = discord.Intents.default()
intents.message_content = True #You'll need to enable this on Discord's website

#Set client
client = discord.Client(intents=intents)

###DON"T FORGET TO SET YOUR BOT TOKEN AT THE BOTTOM###

#
#
###Logged on event
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

#
#
###Read message event
@client.event
async def on_message(message):
    
    #Ignore messages from bot
    if message.author == client.user:
        return
    #
    #
    ###Trivia command
    if message.content.startswith('$trivia'):
        player = message.author
        playerName = str(player)
        print(player,"started trivia.")
        
        #Read files as Pandas dataframes
        playerDF = pd.read_csv( #Player data and leaderboard
            "PlayerData.csv",
            delimiter=","
            )

        questions = pd.read_csv( #Question list
            "Questions.csv",
            index_col="index",
            delimiter=","
            )

        
        #Add player to leaderboard if they aren't already there. """"BUGGED""""
        if playerName not in playerDF["name"].values:
            print("player",playerName,"not in leaderboard, adding them...")
            playerData = { #Build dataframe row to add to leaderboard
                "name": [player],
                "attempts": [0],
                "score": [0]
                }
            playerDataDF = pd.DataFrame(playerData) #Convert to dataframe
            playerDataDF.to_csv( #Write to leaderboard
                "PlayerData.csv", 
                index=False, 
                header=False, 
                mode="a"
                ) 
            playerDF = pd.read_csv( #Re-read variable
                "PlayerData.csv",
                delimiter=","
                )
        

        #Get player data
        playerData = playerDF.loc[playerDF["name"] == playerName] #Data block
        attempts = playerData["attempts"].item()
        
        #Get the current question data
        playerQuestion = questions.loc[attempts]
        question = playerQuestion["question"]
        correctAnswer = playerQuestion["answer"]
        hint = playerQuestion["hint"]
        
        ###Send question message###
        await message.channel.send(question)
        
        #
        #
        ###Trivia Question###
        c = True
        while c:
            #Read response
            print("Awaiting message...")
            message2 = await client.wait_for("message", timeout=60)
            print("Message Recieved!")
            
            #Check if message is from player
            if message2.author == player:
                
                #Check for correct answer
                if message2.content.lower() == correctAnswer:
                    print(playerName," answered correctly!")
                    await message2.channel.send("Correct!") #Send correct message
                    c = False #Stop loop
                    
                
                #Hint command
                elif message2.content.startswith("$hint"):
                    print(playerName," requested a hint.")
                    await message2.channel.send(hint) #Send hint message
                    print("Hint sent for ", playerName)
                #If incorrect
                else:
                    print(playerName," answered incorrectly!")
                    await message2.channel.send("Incorrect.") #Send incorrect message
                    c = False #Stop loop



#DON"T FORGET TO SET YOUR BOT TOKEN!!#
client.run("Your Token Goes Here")