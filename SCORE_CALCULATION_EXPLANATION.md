# Score Calculation Explanation

## How Total Scores Are Calculated

### For Individual Students (Per-Student Scoring)

When a judge evaluates a project, they score each student individually for each criterion. Here's how the total score is calculated:

#### Step 1: Calculate Weighted Score for Each Criterion

For each criterion, the system calculates:
```
Weighted Score = (Student's Score for Criterion) × (Criterion Weight)
```

**Example:**
- Criterion: "Midterm-Evaluation"
- Student's Score: 10.00
- Criterion Weight: 1.0
- Weighted Score = 10.00 × 1.0 = 10.00

#### Step 2: Sum All Weighted Scores

The total score for a student is the sum of all weighted scores:
```
Total Score = Sum of (Weighted Score for each criterion)
```

**Example:**
- Criterion 1 Weighted Score: 10.00
- Criterion 2 Weighted Score: 20.00
- Criterion 3 Weighted Score: 10.00
- **Total Score = 10.00 + 20.00 + 10.00 = 40.00**

#### Step 3: Calculate Percentage

```
Percentage = (Total Score / Max Total Score) × 100
```

**Example:**
- Total Score: 13.33
- Max Total Score: 100.00
- Percentage = (13.33 / 100.00) × 100 = 13.33%

### Example: Seyam's Score of 13.33 / 100

If Seyam has a total score of 13.33 out of 100, this means:

**Possible Scenarios:**

1. **Only some criteria were scored:**
   - Criterion 1: 10.00 (weight: 1.0) → Weighted: 10.00
   - Criterion 2: 3.33 (weight: 1.0) → Weighted: 3.33
   - **Total = 13.33** (other criteria not scored yet)

2. **All criteria scored but with low scores:**
   - Criterion 1: 10.00 (weight: 1.0) → Weighted: 10.00
   - Criterion 2: 2.00 (weight: 1.0) → Weighted: 2.00
   - Criterion 3: 1.33 (weight: 1.0) → Weighted: 1.33
   - **Total = 13.33**

3. **With different weights:**
   - Criterion 1: 10.00 (weight: 0.5) → Weighted: 5.00
   - Criterion 2: 8.33 (weight: 1.0) → Weighted: 8.33
   - **Total = 13.33**

### Average Scores Across Judges

When multiple judges evaluate the same student:

#### Step 1: Calculate Average per Criterion

For each criterion, average all judges' scores:
```
Average Score = Sum of (All Judges' Scores) / Number of Judges
```

**Example:**
- Judge 1 gave: 10.00
- Judge 2 gave: 15.00
- Average = (10.00 + 15.00) / 2 = 12.50

#### Step 2: Calculate Weighted Average

```
Weighted Average = Average Score × Criterion Weight
```

#### Step 3: Sum Weighted Averages

```
Total Average = Sum of (Weighted Average for each criterion)
```

## Formula Summary

### For a Single Judge's Evaluation of One Student:

```
Total Score = Σ (Score[i] × Weight[i])
where i = each criterion
```

### For Average Across Multiple Judges:

```
Average Total = Σ (Average_Score[i] × Weight[i])
where Average_Score[i] = (Sum of all judges' scores for criterion i) / Number of judges
```

## How to Verify Seyam's Score

To understand how Seyam got 13.33:

1. **Check the evaluation detail page:**
   - Go to the evaluation
   - Find Seyam's section
   - Look at each criterion score and its weighted value

2. **Manual calculation example:**
   ```
   If the rubric has these criteria:
   - Criterion 1: Max 30, Weight 1.0
   - Criterion 2: Max 20, Weight 1.0  
   - Criterion 3: Max 25, Weight 1.0
   - Criterion 4: Max 25, Weight 1.0
   
   And Seyam received:
   - Criterion 1: 10.00 → Weighted: 10.00 × 1.0 = 10.00
   - Criterion 2: 3.33 → Weighted: 3.33 × 1.0 = 3.33
   - Criterion 3: 0.00 (not scored) → Weighted: 0.00
   - Criterion 4: 0.00 (not scored) → Weighted: 0.00
   
   Total = 10.00 + 3.33 + 0.00 + 0.00 = 13.33
   ```

3. **If Max Total Score is 100:**
   - This means the rubric's `max_total_score` is set to 100
   - Or the sum of (Max Score × Weight) for all criteria = 100

## Maximum Score Calculation

The maximum possible score is calculated as:
```
Max Total Score = Σ (Max_Score[i] × Weight[i])
```

**Example:**
- Criterion 1: Max 30, Weight 1.0 → Max Weighted: 30.00
- Criterion 2: Max 20, Weight 1.0 → Max Weighted: 20.00
- Criterion 3: Max 25, Weight 1.0 → Max Weighted: 25.00
- Criterion 4: Max 25, Weight 1.0 → Max Weighted: 25.00
- **Max Total = 30 + 20 + 25 + 25 = 100.00**

Or if `max_total_score` is explicitly set in the rubric, that value is used.

## Common Questions

### Q: Why is my score lower than expected?
**A:** Check if:
- All criteria were scored (some might be 0 or missing)
- The scores given are actually low
- Weights are reducing the scores

### Q: How do I see the breakdown?
**A:** In the evaluation detail page, each student's section shows:
- Each criterion score
- The weighted score for each criterion
- The total sum

### Q: What if multiple judges scored differently?
**A:** The system calculates averages automatically. In reports, you'll see:
- Individual judge scores
- Average scores across all judges
