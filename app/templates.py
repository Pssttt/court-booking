def get_booking_form_html(courts: list, default_time: str = "13:00") -> str:
    court_options = "".join(
        [
            f'<option value="{court["name"]}">{court["name"]}</option>'
            for court in courts
        ]
    )

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Court Booking</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            html, body {{
                height: 100%;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
                background: #ffffff;
                color: #1a1a1a;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }}
            
            .container {{
                width: 100%;
                max-width: 500px;
            }}
            
            header {{
                text-align: center;
                margin-bottom: 40px;
            }}
            
            h1 {{
                font-size: 32px;
                font-weight: 400;
                letter-spacing: -0.5px;
                margin-bottom: 8px;
                color: #000;
            }}
            
            .subtitle {{
                font-size: 14px;
                color: #666;
                font-weight: 400;
            }}
            
            .form-group {{
                margin-bottom: 24px;
            }}
            
            .section {{
                margin-bottom: 32px;
            }}
            
            .section-title {{
                font-size: 13px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                color: #999;
                margin-bottom: 16px;
            }}
            
            label {{
                display: block;
                font-size: 14px;
                font-weight: 500;
                color: #1a1a1a;
                margin-bottom: 6px;
            }}
            
            input, select {{
                width: 100%;
                padding: 10px 12px;
                font-size: 14px;
                font-family: inherit;
                border: 1px solid #ddd;
                background: #fff;
                color: #1a1a1a;
                transition: border-color 0.2s;
                appearance: none;
            }}
            
            input:focus, select:focus {{
                outline: none;
                border-color: #000;
                box-shadow: inset 0 0 0 2px #f5f5f5;
            }}
            
            input::placeholder {{
                color: #999;
            }}
            
            select {{
                padding-right: 32px;
                background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
                background-repeat: no-repeat;
                background-position: right 8px center;
                background-size: 16px;
                padding-right: 32px;
            }}
            
            select::-ms-expand {{
                display: none;
            }}
            
            button {{
                width: 100%;
                padding: 12px 16px;
                font-size: 14px;
                font-weight: 500;
                background: #000;
                color: #fff;
                border: none;
                cursor: pointer;
                transition: background 0.2s, opacity 0.2s;
                margin-top: 16px;
            }}
            
            button:hover {{
                background: #1a1a1a;
            }}
            
            button:active {{
                opacity: 0.8;
            }}
            
            button:disabled {{
                background: #ccc;
                cursor: not-allowed;
            }}
            
            .message {{
                padding: 12px 14px;
                border-radius: 2px;
                font-size: 13px;
                margin-bottom: 20px;
                display: none;
                line-height: 1.5;
            }}
            
            .success {{
                background: #f0f9f0;
                border: 1px solid #b0e0b0;
                color: #1a5a1a;
            }}
            
            .error {{
                background: #fef0f0;
                border: 1px solid #e0b0b0;
                color: #5a1a1a;
            }}
            
            .loading {{
                text-align: center;
                color: #666;
                font-size: 13px;
                margin-top: 16px;
                display: none;
            }}
            
            @media (max-width: 600px) {{
                h1 {{
                    font-size: 24px;
                }}
                
                .container {{
                    padding: 0;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Court Booking</h1>
                <p class="subtitle">Schedule your badminton court</p>
            </header>
            
            <div class="message success" id="success"></div>
            <div class="message error" id="error"></div>
            
            <form id="bookingForm">
                <div class="section">
                    <div class="section-title">Players</div>
                    
                    <div class="form-group">
                        <label for="p1">Player 1</label>
                        <input type="text" id="p1" name="p1" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="p2">Player 2</label>
                        <input type="text" id="p2" name="p2" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="p3">Player 3</label>
                        <input type="text" id="p3" name="p3" required>
                    </div>
                </div>
                
                <div class="section">
                    <div class="form-group">
                        <label for="court">Court</label>
                        <select id="court" name="court" required>
                            <option value="">Select a court</option>
                            {court_options}
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="submitTime">Time</label>
                        <input type="time" id="submitTime" name="submitTime" value="{default_time}" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="confirmationEmail">Confirmation Email (Optional)</label>
                        <input type="email" id="confirmationEmail" name="confirmationEmail" placeholder="your.email@example.com">
                    </div>
                </div>
                
                <button type="submit">Book Court</button>
                <div class="loading" id="loading">Scheduling...</div>
            </form>
        </div>
        
        <script>
            const form = document.getElementById('bookingForm');
            const successMsg = document.getElementById('success');
            const errorMsg = document.getElementById('error');
            const loading = document.getElementById('loading');
            const submitBtn = form.querySelector('button[type="submit"]');
            
            form.addEventListener('submit', async (e) => {{
                e.preventDefault();
                
                successMsg.style.display = 'none';
                errorMsg.style.display = 'none';
                loading.style.display = 'block';
                submitBtn.disabled = true;
                
                const formData = {{
                    p1: document.getElementById('p1').value,
                    p2: document.getElementById('p2').value,
                    p3: document.getElementById('p3').value,
                    court: document.getElementById('court').value,
                    submit_time: document.getElementById('submitTime').value,
                    confirmation_email: document.getElementById('confirmationEmail').value || null,
                }};
                
                try {{
                    const response = await fetch('/api/book', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify(formData)
                    }});
                    
                    const data = await response.json();
                    
                    if (response.ok) {{
                        successMsg.innerHTML = `Booking confirmed for ${{formData.p1}}, ${{formData.p2}}, ${{formData.p3}} at ${{formData.submit_time}}`;
                        successMsg.style.display = 'block';
                        form.reset();
                        document.getElementById('submitTime').value = '{default_time}';
                    }} else {{
                        errorMsg.innerHTML = `Error: ${{data.detail || 'Failed to schedule booking'}}`;
                        errorMsg.style.display = 'block';
                    }}
                }} catch (error) {{
                    errorMsg.innerHTML = `Error: ${{error.message}}`;
                    errorMsg.style.display = 'block';
                }} finally {{
                    loading.style.display = 'none';
                    submitBtn.disabled = false;
                }}
            }});
        </script>
    </body>
    </html>
    """
