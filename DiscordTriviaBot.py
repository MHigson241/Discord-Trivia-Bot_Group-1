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
    ###Help command
    if message.content.startswith('$help'):
        await message.channel.send("--$trivia: Start trivia.\n--$leaderboard: View top 5 players.\n--$mydata: See your player data.\n--$reset: Reset your player data.")
    
    #
    #
    ###Leaderboard command
    if message.content.startswith('$leaderboard'):
        
        #Read player data file
        playerDF = pd.read_csv(
            "PlayerData.csv",
            delimiter=","
            )
        
        #Make leaderboard
        leaderboard = playerDF.sort_values(by="score", ascending=False)
        leaderboard.reset_index(drop=True, inplace=True)
        
        #Build leaderboard message
        index = 0
        leaderboardMessage = ""
        while index < 5 and index < len(leaderboard):
            leaderboardMessage += str(str(index+1)+": "+leaderboard.at[index,"name"]+
                                      "\n   Questions Attempted: "+str(leaderboard.at[index, "attempts"].item())+
                                      "\n   Correct Answers: "+str(leaderboard.at[index,"cAnswers"].item())+
                                      "\n   Incorrect Answers: "+str(leaderboard.at[index,"attempts"].item() - leaderboard.at[index,"cAnswers"].item())+
                                      "\n   Correct Rate: "+str(round(leaderboard.at[index,"cAnswers"].item() / leaderboard.at[index,"attempts"].item() *100 ,2))+"%"+
                                      "\n   Score: "+str(leaderboard.at[index,"score"].item())+"\n")
            index += 1
            
        #Send leaderboard message
        await message.channel.send(leaderboardMessage)
    
    #
    #
    ###Player data command
    if message.content.startswith('$mydata'):
        
        #Read player data file
        playerDF = pd.read_csv(
            "PlayerData.csv",
            delimiter=","
            )
        
        #Get players data
        playerData = playerDF.loc[playerDF["name"] == "dalsiran"]
        
        #Send player data message
        await message.channel.send("Data for "+playerData["name"].item()+
                                   ":\nQuestions Attempted: "+str(playerData["attempts"].item())+
                                   "\nCorrect Answers: "+str(playerData["cAnswers"].item())+
                                   "\nIncorrect Answers: "+str(playerData["attempts"].item() - playerData["cAnswers"].item())+
                                   "\nCorrect Rate: "+str(round(playerData["cAnswers"].item() / playerData["attempts"].item() *100 ,2))+"%"+
                                   "\nScore: "+str(playerData["score"].item()))
    
    #
    #
    ###Reset command
    if message.content.startswith("$reset"): #Check for reset command
        
        #Get player name
        player = message.author
        playerName = str(player)
        
        #Read player data file
        playerDF = pd.read_csv(
            "PlayerData.csv",
            delimiter=","
            )
        
        print("Deleting player data for...", playerName)
        playerDF = playerDF[playerDF["name"] != playerName] #remove player
        await message.channel.send("Data reset!")
        
        #Write data to leaderboard
        playerDF.to_csv( 
            "PlayerData.csv", 
            index=False
            )
    
    #
    #
    ###Trivia command
    if message.content.startswith('$trivia'):
        player = message.author
        playerName = str(player)
        print(player,"started trivia.")
        
        #Read files as Pandas dataframes
        playerDF = pd.read_csv( #Player data
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
                "cAnswers" : [0],
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
        
        #Check if player has finished the question list
        if attempts >= len(questions):
            
            #Ask if they want to reset their progress
            print(playerName,"has completed trivia! Asking if they want to reset...")
            await message.channel.send("Congrats! You've finished the question list!!! \nWould you like to reset your progress? \n--$reset to reset progress.")
            print("Awaiting response...")
            reset = await client.wait_for("message", timeout=60)
            
            #Reset player data
            if reset.author == player: #Ignore messages not from the player
                if reset.content.startswith("$reset"): #Check for reset command
                    print("Deleting player data for...", playerName)
                    playerDF = playerDF[playerDF["name"] != playerName] #remove player
                    await reset.channel.send("Data reset!")
                    
                    #Write data to leaderboard
                    playerDF.to_csv( 
                        "PlayerData.csv", 
                        index=False
                        )
        else:
        
            #Get the current question data
            playerQuestion = questions.loc[attempts]
            question = str(playerQuestion["question"])
            correctAnswer = playerQuestion["answer"]
            hint = playerQuestion["hint"]
        
            ###Send question message###
            await message.channel.send(question+"\n--$hint to get a hint.\n--$reset to reset your progress.")
        
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
                        playerDF.loc[playerDF["name"] == playerName, "attempts"] += 1
                        playerDF.loc[playerDF["name"] == playerName, "score"] += 1
                        playerDF.loc[playerDF["name"] == playerName, "cAnswers"] += 1
                        c = False #Stop loop
                
                    #Hint command
                    elif message2.content.startswith("$hint"):
                        print(playerName," requested a hint.")
                        await message2.channel.send(hint) #Send hint message
                        print("Hint sent for ", playerName)
                    
                    #Reset command
                    elif message2.content.startswith("$reset"):
                        playerDF = playerDF[playerDF["name"] != playerName]
                        print("Deleting player data for...",playerName)
                        await message2.channel.send("Data reset!")
                        c = False
                    
                    #If incorrect
                    else:
                        print(playerName," answered incorrectly!")
                        await message2.channel.send("Incorrect.") #Send incorrect message
                        playerDF.loc[playerDF["name"] == playerName, "attempts"] += 1
                        playerDF.loc[playerDF["name"] == playerName, "score"] += -1
                        c = False #Stop loop
                
                
                    #Write data to leaderboard
                    print("Writing player data to file...")
                    playerDF.to_csv( 
                        "PlayerData.csv", 
                        index=False
                        )
                    print("Writing complete!")
    

#DON"T FORGET TO SET YOUR BOT TOKEN!!#
client.run("YOUR TOKEN GOES HERE")