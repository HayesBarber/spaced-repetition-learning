# Spaced Repetition Learning

## High level overview

Spaced repetition is a learning technique that involves reviewing material at increasing intervals to improve long-term retention, and this is a CLI tool built around this idea. The primary use case is to better learn data-structures and algorithms via leetcode problems.

When you try a leetcode problem, you give it a rating 1-5. A 1 rating means you did not solve it (or looked at the solution), and a 5 means you solved it flawlessly. The rating will be used as the number of days before you should re-attempt the problem. For example, a 1 rating means you should try the problem again tomorrow, a 2 rating means in two days, and so on. If you manage to rate a problem with 5 two consecutive times, the problem is considered mastered, and it removed from the list.

## Functional requirements

- A user can add a problem they attempted to the list, passing in the problem name and their rating
- A user can append a new rating to a problem based on a re-attempt
- A user can see what problems they should work on today based on their previous ratings. For instance, if the user rating a problem as a 1 yesterday, it should be in the list for today
- The user ask for "n" next problems. For example, only list the top 3 problems based on rating and last attempt.
- The user can see the list of problems they have mastered

## Non-functional requirements

- The tool should be written in python
- The cli command should be "spl"
- The problems in progress should written to a json file
- When a problem is mastered, it should be moved to a separate json file
- When listing problems, the tool should prioritize by last attempt, and then rating. For example, if the user rating a problem as a 1 two days ago, and a different problem as a 1 yesterday, the problem from two days ago should be higher in the list.
- The same command will be used to update rating as to add problems for the first time. When updating an attempt, the tool should not overwrite the rating, but rather append to a list as to not lose previous ratings.
