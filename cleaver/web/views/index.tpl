% from string import ascii_lowercase as ALPHA

<h1>Cleaver Experiments</h1>

% for e in backend.all_experiments():
    <h2>{{e.name}} - {{e.participants}} Participant(s)</h2>

    <p>
        Started {{e.started_on.strftime('%a, %b %d, %Y').replace(' 0', ' ')}}
    </p>

    <table>
        <tr>
            <th></th>
            <th></th>
            <th>Participants</th>
            <th>Conversions</th>
        </tr>
        % for i, v in enumerate(e.variants):
            <tr>
                <td><b>Option {{ALPHA[i].upper()}}:</b></td>
                <td>{{v}}</td>
                <td>-</td>
                <td>-</td>
            </tr>
        % end
    </table>
% end
