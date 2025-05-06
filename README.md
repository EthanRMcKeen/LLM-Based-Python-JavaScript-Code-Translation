# LLM Based Python-JavaScript Code Translation Project

## Generate Synthetic Tests

Use an LLM to generate 5 test cases for each data sample. Prompts include only instructions and the original function, no descriptions or example test cases are provided.

Test cases that take more than 5 seconds to execute or does not pass on original function from dataset are categorized as failed.

Performance Summary Gemini-2.0-Flash

Out of 164 Python functions, the test case pass distribution is as follows:

<table>
  <thead>
    <tr>
      <th style="border: 1px solid; text-align: center;">Number of Test Cases Passed</th>
      <th style="border: 1px solid; text-align: center;">Number of Python Functions</th>
      <th style="border: 1px solid; text-align: center;">Number of JavaScript Functions</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border: 1px solid; text-align: center;">5</td>
      <td style="border: 1px solid; text-align: center;">96</td>
      <td style="border: 1px solid; text-align: center;">96</td>
    </tr>
    <tr>
      <td style="border: 1px solid; text-align: center;">4</td>
      <td style="border: 1px solid; text-align: center;">27</td>
      <td style="border: 1px solid; text-align: center;">30</td>
    </tr>
    <tr>
      <td style="border: 1px solid; text-align: center;">3</td>
      <td style="border: 1px solid; text-align: center;">25</td>
      <td style="border: 1px solid; text-align: center;">19</td>
    </tr>
    <tr>
      <td style="border: 1px solid; text-align: center;">2</td>
      <td style="border: 1px solid; text-align: center;">7</td>
      <td style="border: 1px solid; text-align: center;">6</td>
    </tr>
    <tr>
      <td style="border: 1px solid; text-align: center;">1</td>
      <td style="border: 1px solid; text-align: center;">6</td>
      <td style="border: 1px solid; text-align: center;">6</td>
    </tr>
    <tr>
      <td style="border: 1px solid; text-align: center;">0</td>
      <td style="border: 1px solid; text-align: center;">3</td>
      <td style="border: 1px solid; text-align: center;">7</td>
    </tr>
  </tbody>
</table>

Performance Summary GPT-3.5-Turbo

Out of 164 Python functions, the test case pass distribution is as follows:

<table>
  <thead>
    <tr>
      <th style="border: 1px solid; text-align: center;">Number of Test Cases Passed</th>
      <th style="border: 1px solid; text-align: center;">Number of Python Functions</th>
      <th style="border: 1px solid; text-align: center;">Number of JavaScript Functions</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border: 1px solid; text-align: center;">5</td>
      <td style="border: 1px solid; text-align: center;">65</td>
      <td style="border: 1px solid; text-align: center;">55</td>
    </tr>
    <tr>
      <td style="border: 1px solid; text-align: center;">4</td>
      <td style="border: 1px solid; text-align: center;">32</td>
      <td style="border: 1px solid; text-align: center;">34</td>
    </tr>
    <tr>
      <td style="border: 1px solid; text-align: center;">3</td>
      <td style="border: 1px solid; text-align: center;">24</td>
      <td style="border: 1px solid; text-align: center;">20</td>
    </tr>
    <tr>
      <td style="border: 1px solid; text-align: center;">2</td>
      <td style="border: 1px solid; text-align: center;">16</td>
      <td style="border: 1px solid; text-align: center;">21</td>
    </tr>
    <tr>
      <td style="border: 1px solid; text-align: center;">1</td>
      <td style="border: 1px solid; text-align: center;">13</td>
      <td style="border: 1px solid; text-align: center;">17</td>
    </tr>
    <tr>
      <td style="border: 1px solid; text-align: center;">0</td>
      <td style="border: 1px solid; text-align: center;">14</td>
      <td style="border: 1px solid; text-align: center;">17</td>
    </tr>
  </tbody>
</table>


## Translate Code

Translation Accuracy Summary Gemini-2.0-Flash

<table>
  <thead>
    <tr>
      <th style="border: 1px solid; text-align: center;">Prompt Type</th>
      <th style="border: 1px solid; text-align: center;">Direction</th>
      <th style="border: 1px solid; text-align: center;">Passes</th>
      <th style="border: 1px solid; text-align: center;">Total</th>
      <th style="border: 1px solid; text-align: center;">Accuracy</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="2" style="border: 1px solid; text-align: center;">Baseline Prompting</td>
      <td style="border: 1px solid; text-align: center;">Python → JavaScript</td>
      <td style="border: 1px solid; text-align: center;">144</td>
      <td style="border: 1px solid; text-align: center;">164</td>
      <td style="border: 1px solid; text-align: center;">87.80%</td>
    </tr>
    <tr>
      <td style="border: 1px solid; text-align: center;">JavaScript → Python</td>
      <td style="border: 1px solid; text-align: center;">144</td>
      <td style="border: 1px solid; text-align: center;">164</td>
      <td style="border: 1px solid; text-align: center;">87.80%</td>
    </tr>
    <tr>
      <td rowspan="2" style="border: 1px solid; text-align: center;">With Synthetic Tests<br><span style="font-size: 0.9em;">(only passed tests included)</span></td>
      <td style="border: 1px solid; text-align: center;">Python → JavaScript</td>
      <td style="border: 1px solid; text-align: center;">149</td>
      <td style="border: 1px solid; text-align: center;">164</td>
      <td style="border: 1px solid; text-align: center;">90.85%</td>
    </tr>
    <tr>
      <td style="border: 1px solid; text-align: center;">JavaScript → Python</td>
      <td style="border: 1px solid; text-align: center;">146</td>
      <td style="border: 1px solid; text-align: center;">164</td>
      <td style="border: 1px solid; text-align: center;">89.02%</td>
    </tr>
    <tr>
      <td rowspan="2" style="border: 1px solid; text-align: center;">With Ground Truth Tests</td>
      <td style="border: 1px solid; text-align: center;">Python → JavaScript</td>
      <td style="border: 1px solid; text-align: center;">146</td>
      <td style="border: 1px solid; text-align: center;">164</td>
      <td style="border: 1px solid; text-align: center;">89.02%</td>
    </tr>
    <tr>
      <td style="border: 1px solid; text-align: center;">JavaScript → Python</td>
      <td style="border: 1px solid; text-align: center;">149</td>
      <td style="border: 1px solid; text-align: center;">164</td>
      <td style="border: 1px solid; text-align: center;">90.85%</td>
    </tr>
  </tbody>
</table>

Translation Accuracy Summary GPT-3.5-Turbo-0125

<table>
  <thead>
    <tr>
      <th style="border: 1px solid; text-align: center;">Prompt Type</th>
      <th style="border: 1px solid; text-align: center;">Direction</th>
      <th style="border: 1px solid; text-align: center;">Passes</th>
      <th style="border: 1px solid; text-align: center;">Total</th>
      <th style="border: 1px solid; text-align: center;">Accuracy</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="2" style="border: 1px solid; text-align: center;">Baseline Prompting</td>
      <td style="border: 1px solid; text-align: center;">Python → JavaScript</td>
      <td style="border: 1px solid; text-align: center;">69</td>
      <td style="border: 1px solid; text-align: center;">164</td>
      <td style="border: 1px solid; text-align: center;">42.07%</td>
    </tr>
    <tr>
      <td style="border: 1px solid; text-align: center;">JavaScript → Python</td>
      <td style="border: 1px solid; text-align: center;">77</td>
      <td style="border: 1px solid; text-align: center;">164</td>
      <td style="border: 1px solid; text-align: center;">46.59%</td>
    </tr>
    <tr>
      <td rowspan="2" style="border: 1px solid; text-align: center;">With Synthetic Tests<br><span style="font-size: 0.9em;">(only passed tests included)</span></td>
      <td style="border: 1px solid; text-align: center;">Python → JavaScript</td>
      <td style="border: 1px solid; text-align: center;">80</td>
      <td style="border: 1px solid; text-align: center;">164</td>
      <td style="border: 1px solid; text-align: center;">48.78%</td>
    </tr>
    <tr>
      <td style="border: 1px solid; text-align: center;">JavaScript → Python</td>
      <td style="border: 1px solid; text-align: center;">105</td>
      <td style="border: 1px solid; text-align: center;">164</td>
      <td style="border: 1px solid; text-align: center;">64.02%</td>
    </tr>
    <tr>
      <td rowspan="2" style="border: 1px solid; text-align: center;">With Ground Truth Tests</td>
      <td style="border: 1px solid; text-align: center;">Python → JavaScript</td>
      <td style="border: 1px solid; text-align: center;">101</td>
      <td style="border: 1px solid; text-align: center;">164</td>
      <td style="border: 1px solid; text-align: center;">61.59%</td>
    </tr>
    <tr>
      <td style="border: 1px solid; text-align: center;">JavaScript → Python</td>
      <td style="border: 1px solid; text-align: center;">115</td>
      <td style="border: 1px solid; text-align: center;">164</td>
      <td style="border: 1px solid; text-align: center;">70.12%</td>
    </tr>
  </tbody>
</table>