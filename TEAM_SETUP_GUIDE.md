# Team and Student Setup Guide

## Overview

This guide explains how to add students to teams and assign teams to projects in the Graduation Project Evaluation System.

## Data Structure

```
Project (1) ──────< (1) Team ──────< (Many) Students
```

- **One Project** has **One Team**
- **One Team** has **Many Students** (3 or more)
- **Students** are linked to Teams via ForeignKey

## Step-by-Step Instructions

### Step 1: Create a Project

1. Go to **Admin Panel** → **Projects** → **Add Project**
2. Fill in:
   - **Title**: e.g., "AI-Powered Learning System"
   - **Description**: Project description (optional)
   - **Rubric**: Select a rubric (can be assigned later)
   - **Status**: Choose Draft, Evaluating, or Completed
   - **Created by**: Will be set automatically if you're logged in as admin
3. Click **Save**

### Step 2: Create Student User Accounts

1. Go to **Admin Panel** → **Users** → **Add User**
2. For each student, create a user:
   - **Username**: e.g., "student1", "john.doe"
   - **Password**: Set a password (students can change later)
   - **Email**: Student's email address
   - **Role**: Select **"STUDENT"** (important!)
   - **First name**, **Last name**: Optional but recommended
3. Click **Save and add another** to create multiple students
4. Repeat for all team members

### Step 3: Create Student Profiles

1. Go to **Admin Panel** → **Students** → **Add Student**
2. For each student user, create a student profile:
   - **User**: Select the student user you created (type username to search)
   - **Student ID**: Unique ID, e.g., "2024001", "STU-001"
   - **Team**: Leave empty for now (we'll assign it in the next step)
3. Click **Save and add another** for each student
4. Repeat for all students

### Step 4: Create a Team and Link to Project

1. Go to **Admin Panel** → **Teams** → **Add Team**
2. Fill in:
   - **Project**: Select the project you created in Step 1
   - **Team name**: e.g., "Team Alpha", "Team 1" (optional)
3. Click **Save**

**Note**: Only one team can be linked to each project (OneToOne relationship).

### Step 5: Assign Students to the Team

You can assign students to the team in two ways:

#### Option A: Edit Each Student (Recommended)

1. Go to **Admin Panel** → **Students**
2. Click on a student to edit
3. In the **Team** field, select the team you created
4. Click **Save**
5. Repeat for all students in the team

#### Option B: Filter and Bulk Assign (If Many Students)

1. Go to **Admin Panel** → **Students**
2. Edit each student individually and assign to the team

**Note**: A student can only belong to one team at a time.

## Example Workflow

Let's say you want to create a project "Online Shopping System" with 3 students:

1. **Create Project**: 
   - Title: "Online Shopping System"
   - Status: "Draft"

2. **Create 3 Users**:
   - User 1: username="alice", role="STUDENT"
   - User 2: username="bob", role="STUDENT"
   - User 3: username="charlie", role="STUDENT"

3. **Create 3 Student Profiles**:
   - Student 1: user=alice, student_id="2024001"
   - Student 2: user=bob, student_id="2024002"
   - Student 3: user=charlie, student_id="2024003"

4. **Create Team**:
   - Project: "Online Shopping System"
   - Team name: "Team E-Commerce"

5. **Assign Students to Team**:
   - Edit Alice's student profile → Team: "Team E-Commerce"
   - Edit Bob's student profile → Team: "Team E-Commerce"
   - Edit Charlie's student profile → Team: "Team E-Commerce"

## Verification

After setup, verify everything is correct:

1. **Check Project**:
   - Go to Projects → View your project
   - Should show the team name and team members

2. **Check Team**:
   - Go to Teams → View your team
   - Should show "Member count: 3" (or however many students you added)

3. **Check Students**:
   - Go to Students → Filter by team
   - Should see all students assigned to the team

4. **Student Login**:
   - Students can log in and see their project on the Projects page
   - They can view project details and evaluation results

## Common Issues

### Issue: Can't select a team when creating a student
**Solution**: Create the team first, then assign students to it.

### Issue: Student can't see their project
**Solution**: 
- Make sure student's `team` field is set
- Make sure the team's `project` field is set
- Make sure the student user's role is "STUDENT"

### Issue: Want to add more students to a team later
**Solution**: Simply edit existing students or create new ones and assign them to the team.

### Issue: Want to move a student to a different team
**Solution**: Edit the student's profile and change the Team field to the new team.

## Tips

- **Team Names**: Use descriptive names like "Team Alpha", "Team WebDev", etc.
- **Student IDs**: Use consistent format like "2024001", "2024002" for easy identification
- **Bulk Creation**: Create all users first, then all student profiles, then create teams, then assign students
- **Verification**: Always check that students can see their projects after setup

## Relationship Diagram

```
┌──────────┐
│ Project  │
│ "Web App"│
└────┬─────┘
     │ OneToOne
     │
┌────▼─────┐
│  Team    │
│"Team 1"  │
└────┬─────┘
     │ ForeignKey (Many)
     │
     ├──► Student 1 (Alice, 2024001)
     ├──► Student 2 (Bob, 2024002)
     └──► Student 3 (Charlie, 2024003)
```
