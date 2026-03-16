#include <SFML/Graphics.hpp>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <sstream>
#include <cmath>

const int WIDTH = 800;
const int HEIGHT = 600;
const int SIZE = 20;

const int GRID_X = WIDTH / SIZE;
const int GRID_Y = HEIGHT / SIZE;

struct Segment
{
    int x;
    int y;
};

enum GameState
{
    INTRO,
    PLAYING,
    GAMEOVER
};

int main()
{
    srand(static_cast<unsigned>(time(0)));

    sf::RenderWindow window(sf::VideoMode(WIDTH, HEIGHT), "Fool Snake Product");
    window.setFramerateLimit(60);

    GameState state = INTRO;

    std::vector<Segment> snake;
    snake.push_back({10,10});

    Segment food = {rand()%GRID_X, rand()%GRID_Y};

    int dx = 1;
    int dy = 0;
    int score = 0;

    sf::Clock clock;
    float delay = 0.18f;

    float foodPulse = 0;

    sf::RectangleShape block(sf::Vector2f(SIZE-2,SIZE-2));

    sf::Font font;
    if(!font.loadFromFile("arial.ttf"))
        return -1;

    //------------------------------------------------
    // GRID BACKGROUND
    //------------------------------------------------

    sf::VertexArray grid(sf::Lines);

    for(int x=0;x<=WIDTH;x+=SIZE)
    {
        grid.append(sf::Vertex(sf::Vector2f(x,0),sf::Color(50,60,90,60)));
        grid.append(sf::Vertex(sf::Vector2f(x,HEIGHT),sf::Color(50,60,90,60)));
    }

    for(int y=0;y<=HEIGHT;y+=SIZE)
    {
        grid.append(sf::Vertex(sf::Vector2f(0,y),sf::Color(50,60,90,60)));
        grid.append(sf::Vertex(sf::Vector2f(WIDTH,y),sf::Color(50,60,90,60)));
    }

    //------------------------------------------------
    // ARENA BORDER
    //------------------------------------------------

    sf::RectangleShape arenaOuter(sf::Vector2f(WIDTH-4, HEIGHT-4));
    arenaOuter.setPosition(2,2);
    arenaOuter.setFillColor(sf::Color::Transparent);
    arenaOuter.setOutlineThickness(2);
    arenaOuter.setOutlineColor(sf::Color(120,140,255,160));

    sf::RectangleShape arenaGlow(sf::Vector2f(WIDTH-12, HEIGHT-12));
    arenaGlow.setPosition(6,6);
    arenaGlow.setFillColor(sf::Color::Transparent);
    arenaGlow.setOutlineThickness(1);
    arenaGlow.setOutlineColor(sf::Color(80,120,255,80));

    //------------------------------------------------
    // GLASS PANEL GENERATOR
    //------------------------------------------------

    auto makeGlass = [](float w,float h)
    {
        sf::RectangleShape r;
        r.setSize({w,h});
        r.setFillColor(sf::Color(255,255,255,35));
        r.setOutlineColor(sf::Color(255,255,255,90));
        r.setOutlineThickness(1.5f);
        r.setOrigin(w/2,h/2);
        return r;
    };

    //------------------------------------------------
    // INTRO PANEL
    //------------------------------------------------

    sf::RectangleShape introPanel = makeGlass(480,220);
    introPanel.setPosition(WIDTH/2,HEIGHT/2);

    sf::Text title;
    title.setFont(font);
    title.setString("FOOL SNAKE\nPRODUCT");
    title.setCharacterSize(44);
    title.setStyle(sf::Text::Bold);
    title.setFillColor(sf::Color::White);

    auto tb = title.getLocalBounds();
    title.setOrigin(tb.width/2,tb.height/2);
    title.setPosition(WIDTH/2,HEIGHT/2-30);

    sf::Text startText;
    startText.setFont(font);
    startText.setString("Press SPACE to Start");
    startText.setCharacterSize(22);
    startText.setFillColor(sf::Color(220,220,220));

    auto sb = startText.getLocalBounds();
    startText.setOrigin(sb.width/2,sb.height/2);
    startText.setPosition(WIDTH/2,HEIGHT/2+70);

    //------------------------------------------------
    // SCORE PANEL
    //------------------------------------------------

    sf::RectangleShape scorePanel = makeGlass(180,50);
    scorePanel.setOrigin(0,0);
    scorePanel.setPosition(15,15);

    sf::Text scoreText;
    scoreText.setFont(font);
    scoreText.setCharacterSize(22);
    scoreText.setFillColor(sf::Color::White);
    scoreText.setPosition(35,25);

    //------------------------------------------------
    // GAME OVER PANEL
    //------------------------------------------------

    sf::RectangleShape gameOverPanel = makeGlass(420,200);
    gameOverPanel.setPosition(WIDTH/2,HEIGHT/2);

    sf::Text gameOverTitle;
    gameOverTitle.setFont(font);
    gameOverTitle.setString("GAME OVER");
    gameOverTitle.setCharacterSize(48);
    gameOverTitle.setFillColor(sf::Color::White);
    gameOverTitle.setStyle(sf::Text::Bold);

    auto gb = gameOverTitle.getLocalBounds();
    gameOverTitle.setOrigin(gb.width/2,gb.height/2);
    gameOverTitle.setPosition(WIDTH/2,HEIGHT/2-40);

    sf::Text restartText;
    restartText.setFont(font);
    restartText.setString("Press R to Restart");
    restartText.setCharacterSize(24);
    restartText.setFillColor(sf::Color(200,200,200));

    auto rb = restartText.getLocalBounds();
    restartText.setOrigin(rb.width/2,rb.height/2);
    restartText.setPosition(WIDTH/2,HEIGHT/2+40);

    //------------------------------------------------
    // MAIN LOOP
    //------------------------------------------------

    while(window.isOpen())
    {
        sf::Event event;
        while(window.pollEvent(event))
        {
            if(event.type==sf::Event::Closed)
                window.close();
        }

        //---------------------------------------------
        // INTRO
        //---------------------------------------------

        if(state==INTRO)
        {
            if(sf::Keyboard::isKeyPressed(sf::Keyboard::Space))
                state=PLAYING;
        }

        //---------------------------------------------
        // GAMEPLAY
        //---------------------------------------------

        if(state==PLAYING)
        {
            if(sf::Keyboard::isKeyPressed(sf::Keyboard::Up) && dy==0){dx=0;dy=-1;}
            if(sf::Keyboard::isKeyPressed(sf::Keyboard::Down) && dy==0){dx=0;dy=1;}
            if(sf::Keyboard::isKeyPressed(sf::Keyboard::Left) && dx==0){dx=-1;dy=0;}
            if(sf::Keyboard::isKeyPressed(sf::Keyboard::Right) && dx==0){dx=1;dy=0;}

            if(clock.getElapsedTime().asSeconds()>delay)
            {
                Segment head = snake.front();
                head.x+=dx;
                head.y+=dy;

                snake.insert(snake.begin(),head);

                if(head.x<0||head.y<0||head.x>=GRID_X||head.y>=GRID_Y)
                    state=GAMEOVER;

                for(size_t i=1;i<snake.size();i++)
                    if(head.x==snake[i].x&&head.y==snake[i].y)
                        state=GAMEOVER;

                if(head.x==food.x && head.y==food.y)
                {
                    score++;
                    food={rand()%GRID_X,rand()%GRID_Y};
                }
                else
                    snake.pop_back();

                clock.restart();
            }
        }

        //---------------------------------------------
        // RESTART
        //---------------------------------------------

        if(state==GAMEOVER && sf::Keyboard::isKeyPressed(sf::Keyboard::R))
        {
            snake.clear();
            snake.push_back({10,10});
            dx=1; dy=0;
            score=0;
            state=PLAYING;
        }

        //---------------------------------------------
        // FOOD ANIMATION
        //---------------------------------------------

        foodPulse += 0.08f;
        float scale = 1 + std::sin(foodPulse)*0.15f;

        //---------------------------------------------
        // SCORE TEXT
        //---------------------------------------------

        std::stringstream ss;
        ss<<"Score: "<<score;
        scoreText.setString(ss.str());

        //---------------------------------------------
        // DRAW
        //---------------------------------------------

        window.clear(sf::Color(18,22,35));
        window.draw(grid);
        window.draw(arenaGlow);
        window.draw(arenaOuter);

        if(state==INTRO)
        {
            window.draw(introPanel);
            window.draw(title);
            window.draw(startText);
        }

        if(state==PLAYING || state==GAMEOVER)
        {
            // Snake with glow

            for(size_t i=0;i<snake.size();i++)
            {
                auto &s = snake[i];

                sf::RectangleShape glow(sf::Vector2f(SIZE+10,SIZE+10));
                glow.setFillColor(sf::Color(0,255,160,40));
                glow.setPosition(s.x*SIZE-5,s.y*SIZE-5);
                window.draw(glow);

                if(i==0)
                    block.setFillColor(sf::Color(0,255,180));
                else
                    block.setFillColor(sf::Color(0,220,120));

                block.setPosition(s.x*SIZE,s.y*SIZE);
                window.draw(block);
            }

            // Pulsing food

            sf::RectangleShape foodBlock(sf::Vector2f(SIZE-2,SIZE-2));
            foodBlock.setFillColor(sf::Color(255,90,90));
            foodBlock.setOrigin((SIZE-2)/2,(SIZE-2)/2);
            foodBlock.setPosition(food.x*SIZE+SIZE/2, food.y*SIZE+SIZE/2);
            foodBlock.setScale(scale,scale);
            window.draw(foodBlock);

            window.draw(scorePanel);
            window.draw(scoreText);
        }

        if(state==GAMEOVER)
        {
            window.draw(gameOverPanel);
            window.draw(gameOverTitle);
            window.draw(restartText);
        }

        window.display();
    }

    return 0;
}